import sys
import ast
import inspect
import executing.executing

executing.executing.TESTING = 1

from executing import Source


class Tester(object):
    def __init__(self):
        self.decorators = []
        self.__name__ = ""  # weird pypy3.6 thing

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

    def __call__(self, arg, check_func=True):
        ex = self.get_executing(inspect.currentframe().f_back)
        if ex.decorator:
            assert {ex.node} == ex.statements
            self.decorators.append(ex.node.decorator_list.index(ex.decorator))
        else:
            call = ex.node
            self.check(call.args[0], arg)
            if check_func:
                self.check(call.func, self)
            if (
                isinstance(call.parent, (ast.ClassDef, ast.FunctionDef))
                and call in call.parent.decorator_list
            ):
                return self
        return arg

    def __getattr__(self, item):
        node = self.get_node(ast.Attribute)
        self.check(node.value, self)
        assert node.attr == item
        return self

    def __getitem__(self, item):
        node = self.get_node(ast.Subscript)
        self.check(node.value, self)
        self.check(subscript_item(node), item)
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
