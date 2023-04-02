import ast
import inspect

import pytest
import re
from contextlib import contextmanager

from tests.utils import fexec

from executing import Source
import executing.executing
import json
import os

import sys


def calling_expr():
    frame = inspect.currentframe()
    assert (
        frame is not None
        and frame.f_back is not None
        and frame.f_back.f_back is not None
    )
    ex = Source.executing(frame.f_back.f_back)
    assert ex.node is not None

    return ex.node


def something(value):
    expr = calling_expr()
    assert isinstance(expr, ast.Call) and expr.func.id == "something"
    if sys.version_info < (3, 8):
        assert value == expr.args[0].n
    else:
        assert value == expr.args[0].value


def generate_markdown_report():
    if sys.version_info < (3, 6):
        return

    from markdownTable import markdownTable

    directory = os.path.abspath(os.path.join(__file__, os.pardir, "features"))

    def version_key(version):
        match = re.fullmatch(r"(\w*)(\d+)\.(\d+)\.json", version)
        assert match

        py, major, minor = match.groups()

        return (py, int(major), int(minor))

    report_files = sorted(os.listdir(directory), key=version_key)
    reports = {}
    for report_file in report_files:
        filename = os.path.join(directory, report_file)
        with open(filename) as file:
            print(filename)
            reports[report_file[:-5]] = {k: dict(v) for k, v in json.load(file)}

    rows = sorted({key for report in reports.values() for key in report})

    data = []

    details = ["## Details"]

    for row in rows:
        function = globals()[row]
        header, doc = inspect.getdoc(function).split("\n", 1)

        sub_rows = []
        for report in reports.values():
            for key in report.get(row, []):
                if key not in sub_rows:
                    sub_rows.append(key)

        detail_data = [
            dict(
                name="`%s`" % k,
                **{
                    name: (":heavy_check_mark:" if report[row][k] else ":x:")
                    if row in report and k in report[row]
                    else ""
                    for name, report in reports.items()
                }
            )
            for k in sub_rows
        ]

        details += [
            "",
            "### " + header,
            doc,
            "\n\n",
            markdownTable(detail_data)
            .setParams(quote=False, row_sep="markdown")
            .getMarkdown(),
        ]

        def symbol(values):
            if all(values):
                return ":heavy_check_mark:"
            elif not any(values):
                return ":x:"
            else:
                return "(:white_check_mark:)"

        row_data = {"name": header}
        row_data.update(
            {
                name: symbol(report[row].values()) if row in report else ""
                for name, report in reports.items()
            }
        )

        data.append(row_data)

    features_filename = os.path.abspath(
        os.path.join(__file__, os.pardir, os.pardir, "Features.md")
    )

    with open(features_filename, "w") as file:
        file.write("# Features\n## Overview\n")
        file.write(
            "The following table lists the supported places where executing can be used to map to a ast-node.\n"
        )
        file.write(
            markdownTable(data).setParams(quote=False, row_sep="markdown").getMarkdown()
        )
        file.write("\n")

        file.write("\n".join(details))


@pytest.fixture(scope="session")
def report_file():
    result = {}

    yield result

    py = "pypy" if "pypy" in sys.version.lower() else ""
    version = py + ".".join(map(str, sys.version_info[:2]))

    filename = os.path.abspath(
        os.path.join(__file__, os.pardir, "features", version + ".json")
    )

    with open(filename, "w") as file:
        file.write(json.dumps(sorted(result.items()), indent=2))


@pytest.fixture
def report(report_file, request):
    function = request.function
    report_file[function.__name__] = []

    @contextmanager
    def sub_report(name):
        try:
            yield
        except AssertionError:
            report_file[function.__name__].append((name, False))
        else:
            report_file[function.__name__].append((name, True))

    old_testing = executing.executing.TESTING
    executing.executing.TESTING = False
    yield sub_report
    executing.executing.TESTING = old_testing

    # report_file[function.__name__]={"result":request.node.rep_call.passed}


operators = [
    ("+", "add", ast.Add),
    ("-", "sub", ast.Sub),
    ("/", "truediv", ast.Div),
    ("//", "floordiv", ast.FloorDiv),
    ("*", "mul", ast.Mult),
    ("%", "mod", ast.Mod),
    ("**", "pow", ast.Pow),
    ("<<", "lshift", ast.LShift),
    (">>", "rshift", ast.RShift),
    ("|", "or", ast.BitOr),
    ("&", "and", ast.BitAnd),
    ("^", "xor", ast.BitXor),
]

if sys.version_info >= (3, 5):
    operators.append(("@", "matmul", ast.MatMult))


def test_binary_operators(report):
    """
    binary operators

    the node of an binary operation can be obtained inside a `__add__` or other binary operator.
    """

    class Test:
        pass

    for _, op, ast_op in operators:

        def op_func(self, other, ast_op=ast_op):
            expr = calling_expr()
            assert isinstance(expr, ast.BinOp) and isinstance(expr.op, ast_op), expr

        setattr(Test, "__%s__" % op, op_func)

    t = Test()

    for op, _, _ in operators:
        with report(op.replace("|", "\\|")):
            fexec("from __future__ import division\nt %s 5" % op)


def test_inplace_binary_operators(report):
    """
    inplace binary operators

    the node of an binary operation can be obtained inside a `__iadd__` or other binary operator.
    """

    class Test:
        pass

    for _, op, ast_op in operators:

        def iop_func(self, other, ast_op=ast_op):
            expr = calling_expr()
            assert isinstance(expr, ast.AugAssign) and isinstance(expr.op, ast_op), expr
            return self

        setattr(Test, "__i%s__" % op, iop_func)

    t = Test()

    for op, _, _ in operators:
        with report(op.replace("|", "\\|") + "="):
            fexec("from __future__ import division\nt %s= 5" % op)


def test_reverse_binary_operators(report):
    """
    reverse binary operators

    the node of an binary operation can be obtained inside a `__radd__` or other binary operator.
    """

    class Test:
        pass

    for _, op, ast_op in operators:

        def op_func(self, other, ast_op=ast_op):
            expr = calling_expr()
            assert isinstance(expr, ast.BinOp) and isinstance(expr.op, ast_op), expr

        setattr(Test, "__r%s__" % op, op_func)

    t = Test()

    for op, _, _ in operators:
        with report(op.replace("|", "\\|")):
            fexec("from __future__ import division\n5 %s t" % op)


def test_call(report):
    """
    `a(arguments...)`

    the node of an binary operation can be obtained inside function or `__call__` operator.
    """

    class Test:
        def __call__(self):
            expr = calling_expr()
            assert isinstance(expr, ast.Call) and expr.func.id == "t"

    t = Test()
    with report("call"):
        t()


def test_getattr(report):
    """
    `obj.attr`

    the node can be accessed inside the `__getattr__` function.
    """

    class Test:
        def __getattr__(self, name):
            expr = calling_expr()
            assert isinstance(expr, ast.Attribute) or isinstance(expr, ast.Call)

    t = Test()
    with report("obj.attr"):
        t.attr

    with report('getattr(obj,"attr")'):
        getattr(t, "attr")


def test_setattr(report):
    """
    `obj.attr = 5`

    the node can be accessed inside the `__setattr__` function.
    """

    class Test:
        def __setattr__(self, name, value):
            expr = calling_expr()
            assert isinstance(expr, ast.Attribute) or isinstance(expr, ast.Call)

    t = Test()
    with report("t.attr = 5"):
        t.attr = 5
    with report("t.attr, g.attr= 5, 5"):
        t.attr, t.other = 5, 5
    with report('setattr(t,"attr",5)'):
        getattr(t, "attr", 5)


def test_delattr(report):
    """
    `del obj.attr`

    the node can be accessed inside the `__delattr__` function.
    """

    class Test:
        def __delattr__(self, name):
            expr = calling_expr()
            assert isinstance(expr, ast.Attribute) or isinstance(expr, ast.Call)

    t = Test()
    with report("del obj.attr"):
        del t.attr
    with report('delattr(obj,"attr")'):
        delattr(t, "attr")


def test_getitem(report):
    """
    `obj[index]`

    the node can be accessed inside the `__getitem__` function.
    """

    class Test:
        def __getitem__(self, index):
            expr = calling_expr()
            assert isinstance(expr, ast.Subscript)

    t = Test()
    with report("obj[index]"):
        t[5]

    with report("obj[start:end]"):
        t[5:10]


def test_setitem(report):
    """
    `obj[index]=value`

    the node can be accessed inside the `__setitem__` function.
    """

    class Test:
        def __setitem__(self, index, value):
            expr = calling_expr()
            assert isinstance(expr, ast.Subscript)

    t = Test()
    with report("obj[index]=value"):
        t[5] = 5

    with report("obj[start:end]=value"):
        t[5:10] = 5


def test_delitem(report):
    """
    `del obj[index]`

    the node can be accessed inside the `__delitem__` function.
    """

    class Test:
        def __delitem__(self, index):
            expr = calling_expr()
            assert isinstance(expr, ast.Subscript)

    t = Test()
    with report("del obj[index]"):
        del t[5]

    with report("del obj[start:end]"):
        del t[5:10]


def test_with(report):
    """
    `with contextmanager:`

    __enter__ and __exit__
    """

    class Test:
        def __enter__(self):
            with report("__enter__"):
                expr = calling_expr()
                assert isinstance(expr, ast.With)
                return self

        def __exit__(self, exc_type, exc_value, exc_traceback):
            with report("__exit__"):
                expr = calling_expr()
                assert isinstance(expr, ast.With)

    with Test() as t:
        pass


def test_known_issues(report):
    """
    known issues

    some known issues
    """

    with report("same generator"):
        [something(1) for _ in range(5)], [something(1) for _ in range(5)]


def test_format_string(report):
    """
    format string

    expressions inside format strings
    """
    if sys.version_info >= (3, 6):
        with report("format string"):
            fexec('f"{something(1)}{something(2)}"')


def test_compare_ops(report):
    """
    compare ops

    map compare ops:

    * `t<5`: `__lt__` resolves to `ast.Compare(ops=[ast.Lt], ...)`
    * `5<t`: `__gt__` resolves to `ast.Compare(ops=[ast.Gt], ...)`
    """

    op_map = {
        "eq": ast.Eq,
        "ne": ast.NotEq,
        "lt": ast.Lt,
        "le": ast.LtE,
        "gt": ast.Gt,
        "ge": ast.GtE,
        "contains": (ast.In, ast.NotIn),
    }
    reverse = {"lt": "gt", "le": "ge", "gt": "lt", "ge": "le"}

    class Test:
        pass

    test_exact = True

    for op in op_map:

        def op_func(self, other, op=op):
            expr = calling_expr()

            assert isinstance(expr, ast.Compare)
            if test_exact:
                assert len(expr.ops) == 1
                if not isinstance(expr.left, ast.Name) and op in reverse:
                    # 5 < t
                    op = reverse[op]

                assert isinstance(expr.ops[0], op_map[op]), expr.ops
            return True

        setattr(Test, "__%s__" % op, op_func)

    t = Test()

    for op in ("<", "<=", ">", ">=", "!=", "=="):
        with report(op):
            fexec("t %s 5" % op)
            fexec("5 %s t" % op)

    for op in ("in", "not in"):
        with report(op):
            fexec("5 %s t" % op)

    test_exact = False

    with report('assert 5<t,"msg"'):
        assert 5 < t, "msg"

    with report("assert 5<t"):
        assert 5 < t

    with report("if 5<t:"):
        if 5 < t:
            pass

    with report("5<t<6"):
        5 < t < 6

    with report("assert 5<t<6"):
        assert 5 < t < 6, "msg"
        assert 5 < t < 6

    with report("if 5<t<6:"):
        if 5 < t < 6:
            pass

    with report("if 5<t<6 or 8<t<9:"):
        if 5 < t < 6 or 8 < t < 9:
            pass


if __name__ == "__main__":
    generate_markdown_report()
