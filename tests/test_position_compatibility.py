import ast
import inspect
import sys
import subprocess

import pytest

from executing import Source


def execute(tmp_path, source, namespace):
    path = tmp_path / "example.py"
    path.write_text(source, encoding="utf-8")
    exec(compile(source, str(path), "exec"), namespace)


@pytest.mark.parametrize(
    "symbol", ["+", "-", "*", "@", "/", "//", "%", "**", "<<", ">>", "&", "^", "|"]
)
@pytest.mark.parametrize(
    "inplace",
    [
        False,
        pytest.param(
            True,
            marks=pytest.mark.skipif(
                sys.version_info < (3, 11),
                reason="Augmented assignment lookup requires Python 3.11 source positions",
            ),
        ),
    ],
)
def test_arithmetic_expression(tmp_path, symbol, inplace):
    results = []

    def operation(self, other):
        results.append(Source.executing(inspect.currentframe().f_back))
        return self

    methods = [
        "add",
        "sub",
        "mul",
        "matmul",
        "truediv",
        "floordiv",
        "mod",
        "pow",
        "lshift",
        "rshift",
        "and",
        "xor",
        "or",
    ]
    probe_type = type(
        "Probe",
        (),
        {
            "__%s%s__" % (prefix, method): operation
            for method in methods
            for prefix in ("", "i")
        },
    )
    source = "probe %s%s 1" % (symbol, "=" if inplace else "")
    execute(tmp_path, source, {"probe": probe_type()})
    (result,) = results
    assert isinstance(result.node, ast.AugAssign if inplace else ast.BinOp)
    assert result.text() == source


@pytest.mark.parametrize(
    "expression",
    [
        "probe.method(1)",
        "probe.method(value=1)",
        "probe.method(*(1,))",
        "probe.method(**{'value': 1})",
        "(probe\n .method)(1)",
        "probe.method(1).method(2)",
    ],
)
def test_method_call_expression(tmp_path, expression):
    results = []

    class Probe:
        def method(self, value):
            results.append(Source.executing(inspect.currentframe().f_back))
            return self

    execute(tmp_path, expression, {"probe": Probe()})
    assert all(isinstance(result.node, ast.Call) for result in results)
    assert results[-1].text() == expression
    if len(results) == 2:
        assert results[0].text() == "probe.method(1)"


def test_unbound_closure_name(tmp_path):
    with pytest.raises(NameError) as error:
        execute(
            tmp_path,
            """
def outer(unrelated):
    closed = 1
    def inner(other):
        return closed
    del closed
    return inner(None)
outer(None)
""",
            {},
        )
    traceback = error.value.__traceback__
    while traceback.tb_next is not None:
        traceback = traceback.tb_next
    result = Source.executing(traceback)
    assert isinstance(result.node, ast.Name)
    assert result.text() == "closed"


@pytest.mark.skipif(
    sys.implementation.name != "pypy" or sys.version_info < (3, 11),
    reason="PyPy cannot represent these source columns",
)
def test_missing_source_columns(tmp_path):
    path = tmp_path / "long_columns.py"
    path.write_text(
        "import inspect\nfrom executing import Source\n"
        "def record():\n"
        "    assert Source.executing(inspect.currentframe().f_back).node is None\n"
        "value =" + " " * 300 + "record()\n",
        encoding="utf-8",
    )
    subprocess.run(
        [
            sys.executable,
            "-c",
            "import runpy, sys; runpy.run_path(sys.argv[1])",
            str(path),
        ],
        check=True,
    )
