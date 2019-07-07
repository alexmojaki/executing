# -*- coding: utf-8 -*-
from __future__ import print_function, division

import ast
import inspect
import os
import sys
import tempfile
import time
import unittest

from executing import Source, only, PY3, NotOneValueFound, get_instructions


class TestStuff(unittest.TestCase):

    # noinspection PyTrailingSemicolon
    def test_semicolons(self):
        # @formatter:off
        tester(1); tester(2); tester(3)
        tester(9
               ); tester(
            8); tester(
            99
        ); tester(33); tester([4,
                               5, 6, [
                                7]])
        # @formatter:on

    def test_decorator(self):
        @empty_decorator
        @decorator_with_args(tester('123'), x=int())
        @tester(list(tuple([1, 2])), returns=empty_decorator)
        @tester(
            list(
                tuple(
                    [3, 4])),
            returns=empty_decorator)
        @empty_decorator
        @decorator_with_args(
            str(),
            x=int())
        @tester(list(tuple([5, 6])), returns=empty_decorator)
        @tester(list(tuple([7, 8])), returns=empty_decorator)
        @empty_decorator
        @decorator_with_args(tester('sdf'), x=tester('123234'))
        def foo():
            pass

    def test_comprehensions(self):
        # Comprehensions can be separated if they contain different names
        str([{tester(x) for x in [1]}, {tester(y) for y in [1]}])
        # or are on different lines
        str([{tester(x) for x in [1]},
             {tester(x) for x in [1]}])
        # or are of different types
        str([{tester(x) for x in [1]}, list(tester(x) for x in [1])])
        # but not if everything is the same
        # noinspection PyTypeChecker
        # with self.assertRaises((AttributeError, NotOneValueFound)):
        #     str([{tester(x) for x in [1]}, {tester(x) for x in [2]}])

    def test_lambda(self):
        self.assertEqual(
            (lambda x: (tester(x), tester(x)))(tester(3)),
            (3, 3),
        )
        (lambda: (lambda: tester(1))())()
        self.assertEqual(
            (lambda: [tester(x) for x in tester([1, 2])])(),
            [1, 2],
        )

    def test_closures_and_nested_comprehensions(self):
        x = 1
        # @formatter:off
        str({tester(a+x): {tester(b+x): {tester(c+x) for c in tester([1, 2])} for b in tester([3, 4])} for a in tester([5, 6])})

        def foo():
            y = 2
            str({tester(a+x): {tester(b+x): {tester(c+x) for c in tester([1, 2])} for b in tester([3, 4])} for a in tester([5, 6])})
            str({tester(a+y): {tester(b+y): {tester(c+y) for c in tester([1, 2])} for b in tester([3, 4])} for a in tester([5, 6])})
            str({tester(a+x+y): {tester(b+x+y): {tester(c+x+y) for c in tester([1, 2])} for b in tester([3, 4])} for a in tester([5, 6])})

            def bar():
                z = 3
                str({tester(a+x): {tester(b+x): {tester(c+x) for c in tester([1, 2])} for b in tester([3, 4])} for a in tester([5, 6])})
                str({tester(a+y): {tester(b+y): {tester(c+y) for c in tester([1, 2])} for b in tester([3, 4])} for a in tester([5, 6])})
                str({tester(a+x+y): {tester(b+x+y): {tester(c+x+y) for c in tester([1, 2])} for b in tester([3, 4])} for a in tester([5, 6])})
                str({tester(a+x+y+z): {tester(b+x+y+z): {tester(c+x+y+z) for c in tester([1, 2])} for b in tester([3, 4])} for a in tester([5, 6])})

            bar()

        foo()
        # @formatter:on

    def test_indirect_call(self):
        dict(x=tester)['x'](tester)(3, check_func=False)

    def test_compound_statements(self):
        with self.assertRaises(TypeError):
            try:
                for _ in tester([1, 2, 3]):
                    while tester(0):
                        pass
                    else:
                        tester(4)
                else:
                    tester(5)
                    raise ValueError
            except tester(ValueError):
                tester(9)
                raise TypeError
            finally:
                tester(10)

        # PyCharm getting confused somehow?
        # noinspection PyUnreachableCode
        str()

        with self.assertRaises(tester(Exception)):
            if tester(0):
                pass
            elif tester(0):
                pass
            elif tester(1 / 0):
                pass

    def test_generator(self):
        def gen():
            for x in [1, 2]:
                yield tester(x)

        gen2 = (tester(x) for x in tester([1, 2]))

        assert list(gen()) == list(gen2) == [1, 2]

    def test_future_import(self):
        tester(4)

    def test_many_calls(self):
        node = None
        start = time.time()
        for i in range(10000):
            new_node = Source.executing(inspect.currentframe()).node
            if node is None:
                node = new_node
            else:
                self.assertIs(node, new_node)
        self.assertLess(time.time() - start, 1)

    def test_decode_source(self):
        def check(source, encoding, exception=None, matches=True):
            encoded = source.encode(encoding)
            if exception:
                with self.assertRaises(exception):
                    Source.decode_source(encoded)
            else:
                decoded = Source.decode_source(encoded)
                if matches:
                    self.assertEqual(decoded, source)
                else:
                    self.assertNotEqual(decoded, source)

        check(u'# coding=utf8\né', 'utf8')
        check(u'# coding=gbk\né', 'gbk')

        check(u'# coding=utf8\né', 'gbk', exception=UnicodeDecodeError)
        check(u'# coding=gbk\né', 'utf8', matches=False)

        # In Python 3 the default encoding is assumed to be UTF8
        if PY3:
            check(u'é', 'utf8')
            check(u'é', 'gbk', exception=SyntaxError)

    def test_multiline_strings(self):
        tester('a')
        tester('''
            ab''')
        tester('''
                    abc
                    def
                    '''
               )
        str([
            tester(
                '''
                123
                456
                '''
            ),
            tester(
                '''
                345
                456786
                '''
            ),
        ])
        tester(
            [
                '''
                123
                456
                '''
                '''
                345
                456786
                '''
                ,
                '''
                123
                456
                ''',
                '''
                345
                456786
                '''
            ]
        )

    def test_multiple_statements_on_one_line(self):
        if tester(1): tester(2)
        for _ in tester([1, 2]): tester(3)

    def assert_qualname(self, func, qn, check_actual_qualname=True):
        qualname = Source.for_filename(__file__).code_qualname(func.__code__)
        self.assertEqual(qn, qualname)
        if PY3 and check_actual_qualname:
            self.assertEqual(qn, func.__qualname__)
        self.assertTrue(qn.endswith(func.__name__))

    def test_qualname(self):
        self.assert_qualname(C.f, 'C.f')
        self.assert_qualname(C.D.g, 'C.D.g')
        self.assert_qualname(f, 'f')
        self.assert_qualname(f(), 'f.<locals>.g')
        self.assert_qualname(C.D.h(), 'C.D.h.<locals>.i.<locals>.j')
        self.assert_qualname(lamb, '<lambda>')
        foo = lambda_maker()
        self.assert_qualname(foo, 'lambda_maker.<locals>.foo')
        self.assert_qualname(foo.x, 'lambda_maker.<locals>.<lambda>')
        self.assert_qualname(foo(), 'lambda_maker.<locals>.foo.<locals>.<lambda>')
        self.assert_qualname(foo()(), 'lambda_maker.<locals>.foo.<locals>.<lambda>', check_actual_qualname=False)

    def test_extended_arg(self):
        source = 'tester(6)\n%s\ntester(9)' % list(range(66000))
        _, filename = tempfile.mkstemp()
        code = compile(source, filename, 'exec')
        with open(filename, 'w') as outfile:
            outfile.write(source)
        exec(code)

    def test_only(self):
        for n in range(5):
            gen = (i for i in range(n))
            if n == 1:
                self.assertEqual(only(gen), 0)
            else:
                with self.assertRaises(NotOneValueFound):
                    only(gen)

    def test_invalid_python(self):
        path = os.path.join(os.path.dirname(__file__), 'not_code.txt', )
        source = Source.for_filename(path)
        self.assertIsNone(source.tree)

    def test_executing_methods(self):
        frame = inspect.currentframe()
        executing = Source.executing(frame)
        self.assertEqual(executing.code_qualname(), 'TestStuff.test_executing_methods')
        if 'pypy' not in sys.version.lower():
            text = 'Source.executing(frame)'
            self.assertEqual(executing.text(), text)
            start, end = executing.text_range()
            self.assertEqual(executing.source.text[start:end], text)

    def test_attr(self):
        c = C()
        c.x = c.y = tester
        str((c.x.x, c.x.y, c.y.x, c.y.y, c.x.asd, c.y.qwe))


class TestFile(unittest.TestCase):
    def test_file(self):
        source = Source.for_frame(inspect.currentframe())
        code = compile(source.text, source.filename, 'exec')
        instructions = get_instructions(code)
        lineno = None
        for inst in instructions:
            if inst.starts_line is not None:
                lineno = inst.starts_line
            if not inst.opname.startswith(
                    ('BINARY_', 'UNARY_', 'LOAD_ATTR', 'LOAD_METHOD', 'LOOKUP_METHOD', 'COMPARE_OP')):
                continue
            frame = C()
            frame.f_lasti = inst.offset
            frame.f_code = code
            frame.f_globals = globals()
            frame.f_lineno = lineno
            print(inst.opname)
            assert Source.executing(frame).node is not None

class C(object):
    @staticmethod
    def f():
        pass

    class D(object):
        @staticmethod
        def g():
            pass

        @staticmethod
        def h():
            def i():
                def j():
                    pass

                return j

            return i()
TestFile().test_file()


def f():
    def g():
        pass

    return g


def lambda_maker():
    def assign(x):
        def decorator(func):
            func.x = x
            return func

        return decorator

    @assign(lambda: 1)
    def foo():
        return lambda: lambda: 3

    return foo


lamb = lambda: 0


class Tester(object):
    def get_node(self, typ):
        frame = inspect.currentframe().f_back.f_back
        Source.lazycache(frame)
        node = Source.executing(frame).node
        assert isinstance(node, typ), (node, typ)
        return node

    def check(self, node, value):
        frame = inspect.currentframe().f_back.f_back
        result = eval(
            compile(ast.Expression(node), frame.f_code.co_filename, 'eval'),
            frame.f_globals,
            frame.f_locals,
        )
        assert result == value, (result, value)

    def __call__(self, arg, check_func=True, returns=None):
        call = self.get_node(ast.Call)
        self.check(call.args[0], arg)
        if check_func:
            self.check(call.func, self)
        if returns is None:
            return arg
        return returns

    def __getattr__(self, item):
        node = self.get_node(ast.Attribute)
        self.check(node.value, self)
        assert node.attr == item
        return self

    def __getitem__(self, item):
        node = self.get_node(ast.Subscript)
        self.check(node.value, self)
        self.check(node.slice.value, item)
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


tester = Tester()


assert tester([1, 2, 3]) == [1, 2, 3]

assert tester.asd is tester
assert tester[19] is tester
assert tester ** 4 is tester
assert tester * 3 is tester
assert tester - 2 is tester
assert tester + 1 is tester
assert -tester is tester
assert +tester is tester
assert ~tester is tester
assert (tester < 7) is tester
assert (tester >= 78) is tester
assert (tester != 79) is tester
# assert (5 != tester != 6) is tester
assert tester.foo(45, False) == 45


def empty_decorator(func):
    return func


def decorator_with_args(*_, **__):
    return empty_decorator


if __name__ == '__main__':
    unittest.main()
