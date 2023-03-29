import subprocess as sp
import sys
import pytest


def run(input):
    p = sp.run(
        [sys.executable, "-m", "IPython", "--colors=nocolor", "--simple-prompt"],
        input=input.encode("utf8"),
        stdout=sp.PIPE,
    )
    output = p.stdout.decode("utf8")
    print(output)
    return output


test_function_code = """
from executing import Source
import inspect
import ast

def test():
    frame = inspect.currentframe()
    ex = Source.executing(frame.f_back)
    print(ex.node)
    if not isinstance(ex.node,ast.Call):
        print("test failure")
    if not ex.node.func.id=="test":
        print("test failure")

"""


@pytest.mark.skipif(sys.version_info < (3,), reason="ipython has no python2.7 support")
def test_one_lookup():
    p = run(test_function_code + "test()")
    assert "test failure" not in p


@pytest.mark.skipif(sys.version_info < (3,), reason="ipython has no python2.7 support")
def test_two_statement_lookups():
    p = run(test_function_code + "test();test()")
    assert "test failure" in p
