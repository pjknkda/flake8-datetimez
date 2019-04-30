__version__ = '19.4.5.0'

import ast
import logging
from collections import namedtuple
from functools import partial

import pycodestyle

LOG = logging.getLogger('flake8.datetimez')


def _get_from_keywords(keywords, arg):
    for keyword in keywords:
        if keyword.arg == arg:
            return keyword


class DateTimeZChecker:
    name = 'flake8.datetimez'
    version = __version__

    def __init__(self, tree, filename):
        self.tree = tree
        self.filename = filename

    def run(self):
        if self.filename in ('stdin', '-', None):
            self.filename = 'stdin'
            self.lines = pycodestyle.stdin_get_value().splitlines(True)
        else:
            self.lines = pycodestyle.readlines(self.filename)

        if not self.tree:
            self.tree = ast.parse(''.join(self.lines))

        for node in ast.walk(self.tree):
            for child_node in ast.iter_child_nodes(node):
                child_node._flake8_datetimez_parent = node

        visitor = DateTimeZVisitor()
        visitor.visit(self.tree)

        for err in visitor.errors:
            yield err


class DateTimeZVisitor(ast.NodeVisitor):

    def __init__(self):
        self.errors = []

    def visit_Call(self, node):
        # ex: `datetime.something()``
        is_datetime_class = (isinstance(node.func, ast.Attribute)
                             and isinstance(node.func.value, ast.Name)
                             and node.func.value.id == 'datetime')

        # ex: `datetime.datetime.something()``
        is_datetime_module_n_class = (isinstance(node.func, ast.Attribute)
                                      and isinstance(node.func.value, ast.Attribute)
                                      and node.func.value.attr == 'datetime'
                                      and isinstance(node.func.value.value, ast.Name)
                                      and node.func.value.value.id == 'datetime')

        if is_datetime_class:
            if node.func.attr == 'datetime':
                # ex `datetime(2000, 1, 1, 0, 0, 0, 0, datetime.timezone.utc)`
                is_case_1 = (len(node.args) == 8
                             and not (isinstance(node.args[7], ast.NameConstant)
                                      and node.args[7].value is None))

                # ex `datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc)`
                tzinfo_keyword = _get_from_keywords(node.keywords, 'tzinfo')
                is_case_2 = (tzinfo_keyword is not None
                             and not (isinstance(tzinfo_keyword.value, ast.NameConstant)
                                      and tzinfo_keyword.value.value is None))

                if not (is_case_1 or is_case_2):
                    self.errors.append(DTZ001(node.lineno, node.col_offset))

        if is_datetime_class or is_datetime_module_n_class:
            if node.func.attr == 'today':
                self.errors.append(DTZ002(node.lineno, node.col_offset))

            elif node.func.attr == 'utcnow':
                self.errors.append(DTZ003(node.lineno, node.col_offset))

            elif node.func.attr == 'utcfromtimestamp':
                self.errors.append(DTZ004(node.lineno, node.col_offset))

            elif node.func.attr in 'now':
                # ex: `datetime.now(UTC)`
                is_case_1 = (len(node.args) == 1
                             and len(node.keywords) == 0
                             and not (isinstance(node.args[0], ast.NameConstant)
                                      and node.args[0].value is None))

                # ex: `datetime.now(tz=UTC)`
                tz_keyword = _get_from_keywords(node.keywords, 'tz')
                is_case_2 = (tz_keyword is not None
                             and not (isinstance(tz_keyword.value, ast.NameConstant)
                                      and tz_keyword.value.value is None))

                if not (is_case_1 or is_case_2):
                    self.errors.append(DTZ005(node.lineno, node.col_offset))

            elif node.func.attr == 'fromtimestamp':
                # ex: `datetime.fromtimestamp(1234, UTC)`
                is_case_1 = (len(node.args) == 2
                             and len(node.keywords) == 0
                             and not (isinstance(node.args[1], ast.NameConstant)
                                      and node.args[1].value is None))

                # ex: `datetime.fromtimestamp(1234, tz=UTC)`
                tz_keyword = _get_from_keywords(node.keywords, 'tz')
                is_case_2 = (tz_keyword is not None
                             and not (isinstance(tz_keyword.value, ast.NameConstant)
                                      and tz_keyword.value.value is None))

                if not (is_case_1 or is_case_2):
                    self.errors.append(DTZ006(node.lineno, node.col_offset))

            elif node.func.attr == 'strptime':
                # ex: `datetime.strptime(...).replace(tzinfo=UTC)`
                parent = getattr(node, '_flake8_datetimez_parent', None)
                pparent = getattr(parent, '_flake8_datetimez_parent', None)
                if not (isinstance(parent, ast.Attribute)
                        and parent.attr == 'replace'):
                    is_case_1 = False
                elif not isinstance(pparent, ast.Call):
                    is_case_1 = False
                else:
                    tzinfo_keyword = _get_from_keywords(pparent.keywords, 'tzinfo')
                    is_case_1 = (tzinfo_keyword is not None
                                 and not (isinstance(tzinfo_keyword.value, ast.NameConstant)
                                          and tzinfo_keyword.value.value is None))

                if not is_case_1:
                    self.errors.append(DTZ007(node.lineno, node.col_offset))

        # ex: `date.something()``
        is_date_class = (isinstance(node.func, ast.Attribute)
                         and isinstance(node.func.value, ast.Name)
                         and node.func.value.id == 'date')

        # ex: `datetime.date.something()``
        is_date_module_n_class = (isinstance(node.func, ast.Attribute)
                                  and isinstance(node.func.value, ast.Attribute)
                                  and node.func.value.attr == 'date'
                                  and isinstance(node.func.value.value, ast.Name)
                                  and node.func.value.value.id == 'datetime')

        if is_date_class or is_date_module_n_class:
            if node.func.attr == 'today':
                self.errors.append(DTZ011(node.lineno, node.col_offset))

            elif node.func.attr == 'fromtimestamp':
                self.errors.append(DTZ012(node.lineno, node.col_offset))

        self.generic_visit(node)


error = namedtuple('error', ['lineno', 'col', 'message', 'type'])
Error = partial(partial, error, type=DateTimeZChecker)

DTZ001 = Error(
    message='DTZ001 The use of `datetime.datetime()` without `tzinfo` argument is not allowed.'
)

DTZ002 = Error(
    message='DTZ002 The use of `datetime.datetime.today()` is not allowed. '
    'Use `datetime.datetime.now(tz=)` instead.'
)

DTZ003 = Error(
    message='DTZ003 The use of `datetime.datetime.utcnow()` is not allowed. '
    'Use `datetime.datetime.now(tz=)` instead.'
)

DTZ004 = Error(
    message='DTZ004 The use of `datetime.datetime.utcfromtimestamp()` is not allowed. '
    'Use `datetime.datetime.fromtimestamp(, tz=)` instead.'
)

DTZ005 = Error(
    message='DTZ005 The use of `datetime.datetime.now()` without `tz` argument is not allowed.'
)

DTZ006 = Error(
    message='DTZ006 The use of `datetime.datetime.fromtimestamp()` without `tz` argument is not allowed.'
)

DTZ007 = Error(
    message='DTZ007 The use of `datetime.datetime.strptime()` must be followed by `.replace(tzinfo=)`.'
)

DTZ011 = Error(
    message='DTZ011 The use of `datetime.date.today()` is not allowed. '
    'Use `datetime.datetime.now(tz=).date()` instead.'
)

DTZ012 = Error(
    message='DTZ012 The use of `datetime.date.fromtimestamp()` is not allowed. '
    'Use `datetime.datetime.fromtimestamp(, tz=).date()` instead.'
)
