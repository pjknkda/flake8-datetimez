__version__ = '19.4.4.0'

import ast
import logging
from collections import namedtuple
from functools import partial

import pycodestyle

LOG = logging.getLogger('flake8.datetimez')


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

        if is_datetime_class or is_datetime_module_n_class:
            if node.func.attr == 'utcnow':
                self.errors.append(DTZ001(node.lineno, node.col_offset))

            elif node.func.attr == 'utcfromtimestamp':
                self.errors.append(DTZ002(node.lineno, node.col_offset))

            elif node.func.attr in 'now':
                # ex: `datetime.now(UTC)`
                is_case_1 = (len(node.args) == 1
                             and len(node.keywords) == 0
                             and not (isinstance(node.args[0], ast.NameConstant)
                                      and node.args[0].value is None))

                # ex: `datetime.now(tz=UTC)`
                is_case_2 = (len(node.args) == 0
                             and len(node.keywords) == 1
                             and node.keywords[0].arg == 'tz'
                             and not (isinstance(node.keywords[0].value, ast.NameConstant)
                                      and node.keywords[0].value.value is None))

                if not (is_case_1 or is_case_2):
                    self.errors.append(DTZ003(node.lineno, node.col_offset))

            elif node.func.attr == 'fromtimestamp':
                # ex: `datetime.fromtimestamp(1234, UTC)`
                is_case_1 = (len(node.args) == 2
                             and len(node.keywords) == 0
                             and not (isinstance(node.args[1], ast.NameConstant)
                                      and node.args[1].value is None))

                # ex: `datetime.fromtimestamp(1234, tz=UTC)`
                is_case_2 = (len(node.args) == 1
                             and len(node.keywords) == 1
                             and node.keywords[0].arg == 'tz'
                             and not (isinstance(node.keywords[0].value, ast.NameConstant)
                                      and node.keywords[0].value.value is None))

                if not (is_case_1 or is_case_2):
                    self.errors.append(DTZ004(node.lineno, node.col_offset))

            elif node.func.attr == 'strptime':
                # ex: `datetime.strptime(...).replace(tzinfo=UTC)`
                parent = getattr(node, '_flake8_datetimez_parent', None)
                pparent = getattr(parent, '_flake8_datetimez_parent', None)
                is_case_1 = (isinstance(parent, ast.Attribute)
                             and parent.attr == 'replace'
                             and isinstance(pparent, ast.Call)
                             and len(pparent.keywords) == 1
                             and pparent.keywords[0].arg == 'tzinfo'
                             and not (isinstance(pparent.keywords[0].value, ast.NameConstant)
                                      and pparent.keywords[0].value.value is None))

                if not is_case_1:
                    self.errors.append(DTZ005(node.lineno, node.col_offset))

        self.generic_visit(node)


error = namedtuple('error', ['lineno', 'col', 'message', 'type'])
Error = partial(partial, error, type=DateTimeZChecker)


DTZ001 = Error(
    message='DTZ001 The use of `datetime.datetime.utcnow()` is not allowed.'
)

DTZ002 = Error(
    message='DTZ002 The use of `datetime.datetime.utcfromtimestamp()` is not allowed.'
)

DTZ003 = Error(
    message='DTZ003 The use of `datetime.datetime.now()` without `tz` argument is not allowed.'
)

DTZ004 = Error(
    message='DTZ004 The use of `datetime.datetime.fromtimestamp()` without `tz` argument is not allowed.'
)

DTZ005 = Error(
    message='DTZ005 The use of `datetime.datetime.strptime()` must be followed by `.replace(tzinfo=)`'
)
