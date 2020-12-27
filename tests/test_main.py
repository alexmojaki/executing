# -*- coding: utf-8 -*-
from __future__ import print_function, division

import ast
import dis
import inspect
import json
import os
import re
import sys
import tempfile
import time
import unittest
from collections import defaultdict
from random import shuffle

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from tests.utils import tester, subscript_item, in_finally

PYPY = 'pypy' in sys.version.lower()

from executing import Source, only, NotOneValueFound
from executing.executing import PY3, get_instructions


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
        with self.assertRaises(NotOneValueFound):
            str([{tester(x) for x in [1]}, {tester(x) for x in [2]}])

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
        print(1 / 2)
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
        text = 'Source.executing(frame)'
        self.assertEqual(executing.text(), text)
        start, end = executing.text_range()
        self.assertEqual(executing.source.text[start:end], text)

    def test_attr(self):
        c = C()
        c.x = c.y = tester
        str((c.x.x, c.x.y, c.y.x, c.y.y, c.x.asd, c.y.qwe))

    def test_traceback(self):
        try:
            134895 / 0
        except:
            tb = sys.exc_info()[2]
            ex = Source.executing(tb)
            self.assertTrue(isinstance(ex.node, ast.BinOp))
            self.assertEqual(ex.text(), "134895 / 0")

    def test_retry_cache(self):
        _, filename = tempfile.mkstemp()

        def check(x):
            source = 'tester(6)\n%s\ntester(9)' % list(range(x))
            code = compile(source, filename, 'exec')
            with open(filename, 'w') as outfile:
                outfile.write(source)
            exec(code, globals(), locals())

        check(3)
        check(5)


def is_unary_not(node):
    return isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not)


class TimeOut(Exception):
    pass


@unittest.skipUnless(
    os.getenv('EXECUTING_SLOW_TESTS'),
    'These tests are very slow, enable them explicitly',
)
class TestFiles(unittest.TestCase):
    def test_files(self):
        self.start_time = time.time()
        root_dir = os.path.dirname(__file__)
        samples_dir = os.path.join(root_dir, 'samples')
        result_filename = PYPY * 'pypy' + sys.version[:3] + '.json'
        result_filename = os.path.join(root_dir, 'sample_results', result_filename)
        result = {}

        for filename in os.listdir(samples_dir):
            full_filename = os.path.join(samples_dir, filename)
            result[filename] = self.check_filename(full_filename)

        if os.getenv('FIX_EXECUTING_TESTS'):
            with open(result_filename, 'w') as outfile:
                json.dump(result, outfile, indent=4, sort_keys=True)
        else:
            with open(result_filename, 'r') as infile:
                self.assertEqual(result, json.load(infile))

        modules = list(sys.modules.values())
        shuffle(modules)
        for module in modules:
            try:
                filename = inspect.getsourcefile(module)
            except TypeError:
                continue

            if not filename:
                continue

            filename = os.path.abspath(filename)

            if (
                    # The sentinel actually appearing in code messes things up
                    'executing' in filename
                    # A file that's particularly slow
                    or 'errorcodes.py' in filename
                    # Contains unreachable code which pypy removes
                    or PYPY and ('sysconfig.py' in filename or 'pyparsing.py' in filename)
            ):
                continue

            try:
                self.check_filename(filename)
            except TimeOut:
                print("Time's up")

    def check_filename(self, filename):
        print(filename)
        source = Source.for_filename(filename)

        if PY3:
            code = compile(source.text, filename, "exec", dont_inherit=True)
            for subcode, qualname in find_qualnames(code):
                if not qualname.endswith(">"):
                    code_qualname = source.code_qualname(subcode)
                    self.assertEqual(code_qualname, qualname)

        nodes = defaultdict(list)
        for node in ast.walk(source.tree):
            if isinstance(node, (
                    ast.UnaryOp,
                    ast.BinOp,
                    ast.Subscript,
                    ast.Call,
                    ast.Compare,
                    ast.Attribute
            )):
                nodes[node] = []

        code = compile(source.tree, source.filename, 'exec')
        result = list(self.check_code(code, nodes))

        if not re.search(r'^\s*if 0(:| and )', source.text, re.MULTILINE):
            for node, values in nodes.items():
                if is_unary_not(node):
                    continue

                if isinstance(getattr(node, 'ctx', None), (ast.Store, ast.Del)):
                    assert not values
                    continue

                if isinstance(node, ast.Compare):
                    if len(node.ops) > 1:
                        assert not values
                        continue

                    if is_unary_not(node.parent) and isinstance(node.ops[0], (ast.In, ast.Is)):
                        continue

                if is_literal(node):
                    continue

                if sys.version_info >= (3, 9) and in_finally(node):
                    correct = len(values) > 1
                else:
                    correct = len(values) == 1

                if not correct:
                    print(source.text, '---', node_string(source, node), node.lineno,
                          len(values), correct, values, file=sys.stderr, sep='\n')
                    self.fail()

        return result

    def check_code(self, code, nodes):
        linestarts = dict(dis.findlinestarts(code))
        instructions = get_instructions(code)
        lineno = None
        for inst in instructions:
            if time.time() - self.start_time > 45 * 60:
                # Avoid travis time limit of 50 minutes
                raise TimeOut

            lineno = linestarts.get(inst.offset, lineno)
            if not inst.opname.startswith((
                    'BINARY_', 'UNARY_', 'LOAD_ATTR', 'LOAD_METHOD', 'LOOKUP_METHOD',
                    'SLICE+', 'COMPARE_OP', 'CALL_', 'IS_OP', 'CONTAINS_OP',
            )):
                continue
            frame = C()
            frame.f_lasti = inst.offset
            frame.f_code = code
            frame.f_globals = globals()
            frame.f_lineno = lineno
            source = Source.for_frame(frame)
            node = None

            try:
                try:
                    node = Source.executing(frame).node
                except Exception:
                    if inst.opname.startswith(('COMPARE_OP', 'CALL_')):
                        continue
                    if isinstance(only(source.statements_at_line(lineno)), (ast.AugAssign, ast.Import)):
                        continue
                    raise
            except Exception:
                print(source.text, lineno, inst, node and ast.dump(node), code, file=sys.stderr, sep='\n')
                raise

            nodes[node].append((inst, frame.__dict__))

            yield [inst.opname, node_string(source, node)]

        for const in code.co_consts:
            if isinstance(const, type(code)):
                for x in self.check_code(const, nodes):
                    yield x


def node_string(source, node):
    return source.asttokens().get_text(node)


def is_literal(node):
    if isinstance(node, ast.UnaryOp):
        return is_literal(node.operand)

    if isinstance(node, ast.BinOp):
        return is_literal(node.left) and is_literal(node.right)

    if isinstance(node, ast.Compare):
        return all(map(is_literal, [node.left] + node.comparators))

    if isinstance(node, ast.Subscript) and is_literal(node.value):
        if isinstance(node.slice, ast.Slice):
            return all(
                x is None or is_literal(x)
                for x in [
                    node.slice.lower,
                    node.slice.upper,
                    node.slice.step,
                ]
            )
        else:
            return is_literal(subscript_item(node))

    try:
        ast.literal_eval(node)
        return True
    except ValueError:
        return False


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


def f():
    def g():
        pass

    return g


# TestFiles().test_files()


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


assert tester([1, 2, 3]) == [1, 2, 3]

assert tester.asd is tester
assert tester[1 + 2] is tester
assert tester ** 4 is tester
assert tester * 3 is tester
assert tester - 2 is tester
assert tester + 1 is tester
assert -tester is +tester is ~tester is tester
assert (tester < 7) is tester
assert (tester >= 78) is tester
assert (tester != 79) is tester
# assert (5 != tester != 6) is tester
assert tester.foo(45, False) == 45

assert (tester or 234) == 234
assert (tester and 1123) is tester


def empty_decorator(func):
    return func


def decorator_with_args(*_, **__):
    return empty_decorator


def find_qualnames(code, prefix=""):
    for subcode in code.co_consts:
        if type(subcode) != type(code):
            continue
        qualname = prefix + subcode.co_name
        instructions = list(get_instructions(subcode))[:4]
        opnames = [inst.opname for inst in instructions]
        arg_reprs = [inst.argrepr for inst in instructions]
        is_class = (
            opnames == "LOAD_NAME STORE_NAME LOAD_CONST STORE_NAME".split()
            and arg_reprs == ["__name__", "__module__", repr(qualname), "__qualname__"]
        )
        yield subcode, qualname
        for x in find_qualnames(
            subcode, qualname + ("." if is_class else ".<locals>.")
        ):
            yield x


if __name__ == '__main__':
    unittest.main()

