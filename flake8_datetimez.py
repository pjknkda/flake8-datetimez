__version__ = "20.10.0"

import ast
from collections import namedtuple
from functools import partial

import pycodestyle


# Every literal is an `ast.Constant` since Python 3.8; the node types it replaced
# (`ast.Str`, ...) are gone in 3.12 and the `ast.Constant.s` alias in 3.14.
def _is_none_constant(node):
    return isinstance(node, ast.Constant) and node.value is None


def _get_from_keywords(keywords, arg):
    for keyword in keywords:
        if keyword.arg == arg:
            return keyword


def _is_datetime_class(node):
    # ex: `datetime.<attr>`, as in `from datetime import datetime`
    return isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "datetime"


def _is_datetime_module_n_class(node):
    # ex: `datetime.datetime.<attr>`
    return (
        isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Attribute)
        and node.value.attr == "datetime"
        and isinstance(node.value.value, ast.Name)
        and node.value.value.id == "datetime"
    )


def _is_followed_by_replace_tzinfo(node):
    # ex: `<node>.replace(tzinfo=UTC)`
    parent = getattr(node, "_flake8_datetimez_parent", None)
    if not (isinstance(parent, ast.Attribute) and parent.attr == "replace"):
        return False

    pparent = getattr(parent, "_flake8_datetimez_parent", None)
    if not isinstance(pparent, ast.Call):
        return False

    tzinfo_keyword = _get_from_keywords(pparent.keywords, "tzinfo")
    return tzinfo_keyword is not None and not _is_none_constant(tzinfo_keyword.value)


def _is_followed_by_astimezone(node):
    # ex: `<node>.astimezone()`
    parent = getattr(node, "_flake8_datetimez_parent", None)
    pparent = getattr(parent, "_flake8_datetimez_parent", None)
    return isinstance(parent, ast.Attribute) and parent.attr == "astimezone" and isinstance(pparent, ast.Call)


class DateTimeZChecker:
    name = "flake8.datetimez"
    version = __version__

    def __init__(self, tree, filename):
        self.tree = tree
        self.filename = filename

    def run(self):
        if not self.tree:
            # flake8 always hands over a parsed tree; reading the source is
            # only needed when the checker is driven directly.
            if self.filename in ("stdin", "-", None):
                lines = pycodestyle.stdin_get_value().splitlines(True)
            else:
                lines = pycodestyle.readlines(self.filename)
            self.tree = ast.parse("".join(lines))

        for node in ast.walk(self.tree):
            for child_node in ast.iter_child_nodes(node):
                child_node._flake8_datetimez_parent = node

        visitor = DateTimeZVisitor()
        visitor.visit(self.tree)

        yield from visitor.errors


class DateTimeZVisitor(ast.NodeVisitor):
    def __init__(self):
        self.errors = []

    def visit_Call(self, node):
        # ex: `datetime.something()``
        is_datetime_class = _is_datetime_class(node.func)

        # ex: `datetime(2000, 1, 1, 0, 0, 0, 0)`
        is_unqualified_datetime_class_call = isinstance(node.func, ast.Name) and node.func.id == "datetime"

        # ex: `datetime.datetime.something()``
        is_datetime_module_n_class = _is_datetime_module_n_class(node.func)

        if (is_datetime_class and node.func.attr == "datetime") or is_unqualified_datetime_class_call:
            # ex `datetime(2000, 1, 1, 0, 0, 0, 0, datetime.timezone.utc)`
            is_case_1 = len(node.args) == 8 and not _is_none_constant(node.args[7])

            # ex `datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc)`
            tzinfo_keyword = _get_from_keywords(node.keywords, "tzinfo")
            is_case_2 = tzinfo_keyword is not None and not _is_none_constant(tzinfo_keyword.value)

            # ex `datetime.datetime(2000, 1, 1).astimezone()`
            is_case_3 = _is_followed_by_astimezone(node)

            if not (is_case_1 or is_case_2 or is_case_3):
                self.errors.append(DTZ001(node.lineno, node.col_offset))

        if is_datetime_class or is_datetime_module_n_class:
            if node.func.attr == "today":
                # ex: `datetime.today().astimezone()`, which reads the naive
                # value as local time -- exactly what `today()` returns
                if not _is_followed_by_astimezone(node):
                    self.errors.append(DTZ002(node.lineno, node.col_offset))

            elif node.func.attr == "utcnow":
                # `.astimezone()` is deliberately not accepted here: it would
                # read the UTC wall clock as local time and shift the instant
                self.errors.append(DTZ003(node.lineno, node.col_offset))

            elif node.func.attr == "utcfromtimestamp":
                # `.astimezone()` is not accepted here either, see DTZ003
                self.errors.append(DTZ004(node.lineno, node.col_offset))

            elif node.func.attr == "now":
                # ex: `datetime.now(UTC)`
                is_case_1 = len(node.args) == 1 and len(node.keywords) == 0 and not _is_none_constant(node.args[0])

                # ex: `datetime.now(tz=UTC)`
                tz_keyword = _get_from_keywords(node.keywords, "tz")
                is_case_2 = tz_keyword is not None and not _is_none_constant(tz_keyword.value)

                # ex: `datetime.now().astimezone()`
                is_case_3 = _is_followed_by_astimezone(node)

                if not (is_case_1 or is_case_2 or is_case_3):
                    self.errors.append(DTZ005(node.lineno, node.col_offset))

            elif node.func.attr == "fromtimestamp":
                # ex: `datetime.fromtimestamp(1234, UTC)`
                is_case_1 = len(node.args) == 2 and len(node.keywords) == 0 and not _is_none_constant(node.args[1])

                # ex: `datetime.fromtimestamp(1234, tz=UTC)`
                tz_keyword = _get_from_keywords(node.keywords, "tz")
                is_case_2 = tz_keyword is not None and not _is_none_constant(tz_keyword.value)

                # ex: `datetime.fromtimestamp(1234).astimezone()`
                is_case_3 = _is_followed_by_astimezone(node)

                if not (is_case_1 or is_case_2 or is_case_3):
                    self.errors.append(DTZ006(node.lineno, node.col_offset))

            elif node.func.attr == "strptime":
                # ex: `datetime.strptime(...).replace(tzinfo=UTC)`
                is_case_1 = _is_followed_by_replace_tzinfo(node)

                # ex: `datetime.strptime(...).astimezone()`
                is_case_2 = _is_followed_by_astimezone(node)

                # ex: `datetime.strptime(..., '...%z...')`
                format_arg = node.args[1] if 1 < len(node.args) else None
                is_case_3 = (
                    isinstance(format_arg, ast.Constant)
                    and isinstance(format_arg.value, str)
                    and "%z" in format_arg.value
                )

                if not (is_case_1 or is_case_2 or is_case_3):
                    self.errors.append(DTZ007(node.lineno, node.col_offset))

        # ex: `date.something()``
        is_date_class = (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "date"
        )

        # ex: `datetime.date.something()``
        is_date_module_n_class = (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Attribute)
            and node.func.value.attr == "date"
            and isinstance(node.func.value.value, ast.Name)
            and node.func.value.value.id == "datetime"
        )

        if is_date_class or is_date_module_n_class:
            if node.func.attr == "today":
                self.errors.append(DTZ011(node.lineno, node.col_offset))

            elif node.func.attr == "fromtimestamp":
                self.errors.append(DTZ012(node.lineno, node.col_offset))

        self.generic_visit(node)

    def visit_Attribute(self, node):
        # ex: `datetime.datetime.min`, `datetime.max`
        if node.attr in ("min", "max") and (_is_datetime_class(node) or _is_datetime_module_n_class(node)):
            if not _is_followed_by_replace_tzinfo(node):
                self.errors.append(DTZ901(node.lineno, node.col_offset))

        self.generic_visit(node)


error = namedtuple("error", ["lineno", "col", "message", "type"])
Error = partial(partial, error, type=DateTimeZChecker)

DTZ001 = Error(message="DTZ001 The use of `datetime.datetime()` without `tzinfo` argument is not allowed.")

DTZ002 = Error(
    message="DTZ002 The use of `datetime.datetime.today()` is not allowed. Use `datetime.datetime.now(tz=)` instead."
)

DTZ003 = Error(
    message="DTZ003 The use of `datetime.datetime.utcnow()` is not allowed. Use `datetime.datetime.now(tz=)` instead."
)

DTZ004 = Error(
    message="DTZ004 The use of `datetime.datetime.utcfromtimestamp()` is not allowed. "
    "Use `datetime.datetime.fromtimestamp(, tz=)` instead."
)

DTZ005 = Error(message="DTZ005 The use of `datetime.datetime.now()` without `tz` argument is not allowed.")

DTZ006 = Error(message="DTZ006 The use of `datetime.datetime.fromtimestamp()` without `tz` argument is not allowed.")

DTZ007 = Error(
    message="DTZ007 The use of `datetime.datetime.strptime()` without %z must be followed by `.replace(tzinfo=)`."
)

DTZ011 = Error(
    message="DTZ011 The use of `datetime.date.today()` is not allowed. Use `datetime.datetime.now(tz=).date()` instead."
)

DTZ012 = Error(
    message="DTZ012 The use of `datetime.date.fromtimestamp()` is not allowed. "
    "Use `datetime.datetime.fromtimestamp(, tz=).date()` instead."
)

DTZ901 = Error(
    message="DTZ901 The use of `datetime.datetime.min` or `datetime.datetime.max` "
    "without `.replace(tzinfo=)` is not allowed."
)
