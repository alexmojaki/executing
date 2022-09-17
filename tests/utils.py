import sys
import ast
import dis
import inspect
from collections import namedtuple

import executing.executing

from executing.executing import attr_names_match

executing.executing.TESTING = 1

from executing import Source

non_existing_argument=object()

class Tester(object):
    def __init__(self):
        self.decorators = []
        self.__name__ = ""  # weird pypy3.6 thing

    def test_set_private_attrs(self):
        # Test that attributes with leading __ are handled properly,
        # as Python mangles their names.
        self.a, self.aa, self._a, self.__a, self.__aa = range(5)

    def check_decorators(self, expected):
        assert self.decorators == expected, (self.decorators, expected)
        self.decorators = []

    def get_node(self, typ):
        ex = self.get_executing(inspect.currentframe().f_back.f_back)
        node = ex.node
        assert isinstance(node, typ), (node, typ)
        return node

    def get_executing(self, frame):
        Source.lazycache(frame)
        return Source.executing(frame)

    def check(self, node, value):
        frame = inspect.currentframe().f_back.f_back
        result = eval(
            compile(ast.Expression(node), frame.f_code.co_filename, 'eval'),
            frame.f_globals,
            frame.f_locals,
        )
        assert result == value, (result, value)

    def __call__(self, arg=non_existing_argument, check_func=True):
        ex = self.get_executing(inspect.currentframe().f_back)
        if ex.decorator:
            assert {ex.node} == ex.statements
            self.decorators.append(ex.node.decorator_list.index(ex.decorator))
        else:
            call = ex.node
            if arg is non_existing_argument:
                assert len(call.args)==0
            else:
                self.check(call.args[0], arg)

            if check_func:
                self.check(call.func, self)
            if (
                isinstance(call.parent, (ast.ClassDef, ast.FunctionDef))
                and call in call.parent.decorator_list
            ):
                return self

        if arg is non_existing_argument:
            return tester
        else:
            return arg

    def __getattr__(self, item):
        parent_frame=inspect.currentframe().f_back

        # pytest is accessing tester to check if it is a test function
        if "_pytest" not in parent_frame.f_code.co_filename:
            node = self.get_node(ast.Attribute)
            self.check(node.value, self)
            assert node.attr == item

        return self

    def __getitem__(self, item):
        node = self.get_node(ast.Subscript)
        self.check(node.value, self)
        self.check(subscript_item(node), item)
        return self

    def __setattr__(self, name, value):
        if name in ('decorators', '__name__'):
            super(Tester, self).__setattr__(name, value)
            return

        node = self.get_node(ast.Attribute)
        self.check(node.value, self)
        if node.attr.startswith('__'):
            # Account for Python's name mangling of private attributes.
            assert name == "_{self.__class__.__name__}{node.attr}".format(self=self, node=node)
        else:
            assert name == node.attr
        assert attr_names_match(node.attr, name)
        return self

    def __delattr__(self, name):
        node = self.get_node(ast.Attribute)
        assert isinstance(node.ctx, ast.Del)
        assert node.attr == name

    def __setitem__(self, key, value):
        node = self.get_node(ast.Subscript)
        self.check(node.value, self)
        if not isinstance(key, slice):
            self.check(subscript_item(node), key)
        return self

    def __add__(self, other):
        node = self.get_node(ast.BinOp)
        self.check(node.left, self)
        self.check(node.right, other)
        return self

    __pow__ = __mul__ = __sub__ = __add__

    def __invert__(self):
        node = self.get_node(ast.UnaryOp)
        self.check(node.operand, self)
        return self

    __neg__ = __pos__ = __invert__

    def __lt__(self, other):
        node = self.get_node(ast.Compare)
        self.check(node.left, self)
        self.check(node.comparators[0], other)
        return self

    __ne__ = __ge__ = __lt__

    def __bool__(self):
        if sys.version_info >= (3, 11):
            self.get_node(ast.BoolOp)
            return False
        else:
            try:
                self.get_node(None)
            except RuntimeError:
                return False
            assert 0

    def __enter__(self):
        self.get_node(ast.With)
        return self

    def __exit__(self, exc_typ, exc_value, exc_traceback):
        self.get_node(ast.With)

    __nonzero__ = __bool__


tester = Tester()


def subscript_item(node):
    if sys.version_info < (3, 9):
        return node.slice.value
    else:
        return node.slice


def in_finally(node):
    while hasattr(node, 'parent'):
        if isinstance(node.parent, ast.Try) and node in node.parent.finalbody:
            return True
        node = node.parent
    return False


SourcePosition = namedtuple("SourcePosition", ["lineno", "col_offset"])


def start_position(obj):
    """
    returns the start source position as a (lineno,col_offset) tuple.
    obj can be ast.AST or dis.Instruction.
    """
    if isinstance(obj, dis.Instruction):
        obj = obj.positions

    if isinstance(obj,ast.Module):
        obj=obj.body[0]

    return SourcePosition(obj.lineno, obj.col_offset)


def end_position(obj):
    """
    returns the end source position as a (lineno,col_offset) tuple.
    obj can be ast.AST or dis.Instruction.
    """
    if isinstance(obj, dis.Instruction):
        obj = obj.positions

    if isinstance(obj,ast.Module):
        obj=obj.body[-1]

    return SourcePosition(obj.end_lineno, obj.end_col_offset)
