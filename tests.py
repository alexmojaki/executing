import ast
import inspect
import unittest

from executing_node import executing_node, only


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

    def test_list_comprehension(self):
        str([tester(int(x)) for x in tester([1]) for _ in tester([2]) for __ in [3]])
        # with self.assertRaises(AssertionError):
        #     str([[[tester(int(x)) for x in tester([1])] for _ in tester([2])] for __ in [3]])
        return str([(1, [
            (2, [
                tester(int(x)) for x in tester([1])])
            for _ in tester([2])])
                    for __ in [3]])

    def test_lambda(self):
        self.assertEqual((lambda x: (tester(x), tester(x)))(tester(3)), (3, 3))
        with self.assertRaises(AssertionError):
            (lambda: (lambda: tester(1))())()
        self.assertEqual((lambda: [tester(x) for x in tester([1, 2])])(), [1, 2])

    def test_indirect_call(self):
        dict(x=tester)['x'](tester)(3)

    def test_compound_statements(self):
        with self.assertRaises(TypeError):
            try:
                for _ in tester([2]):
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


def tester(arg, returns=None):
    frame = inspect.currentframe().f_back
    call = executing_node(frame)
    result = eval(
        compile(ast.Expression(only(call.args)), '<>', 'eval'),
        frame.f_globals,
        frame.f_locals,
    )
    assert result == result, (result, arg)
    if returns is None:
        return arg
    return returns


assert tester([1, 2, 3]) == [1, 2, 3]


def empty_decorator(f):
    return f


def decorator_with_args(*_, **__):
    return empty_decorator


if __name__ == '__main__':
    unittest.main()
