import os
import sys
import inspect
import ast

from littleutils import SimpleNamespace

from executing.executing import is_ipython_cell_code

from executing import Source,NotOneValueFound

sys.path.append(os.path.dirname(os.path.dirname(__file__)))


def test_pytest():
    from tests.utils import tester

    lst = [1, 2, 3]
    lst2 = tester(lst)
    assert lst == lst2
    lst3 = tester(lst + [4])
    assert (
            [1, 2, 3, 4]
            == lst3
    ), 'message'
    x = tester.x
    assert x is tester


def this_expression():
    try:
        return Source.executing(inspect.currentframe().f_back).node
    except NotOneValueFound:
        # TODO: python < 3.11 raises an exception. Should we do the same for the PositionNodeFinder instead of returning None?
        return None


def test_assert():
    assert isinstance(this_expression(),(ast.Call, type(None)))


def test_ipython_cell_code():
    assert is_ipython_cell_code(
        SimpleNamespace(
            co_name="<cell line: 1>",
            co_filename="tmp/ipykernel_3/foo",
        )
    )

    assert not is_ipython_cell_code(
        SimpleNamespace(
            co_name="<cell line: 1",
            co_filename="tmp/ipykernel_3/foo",
        )
    )

    assert not is_ipython_cell_code(
        SimpleNamespace(
            co_name="<cell line: 1>",
            co_filename="tmp/ipykernel_3",
        )
    )
