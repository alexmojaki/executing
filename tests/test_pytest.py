import os
import sys
from time import sleep

from littleutils import SimpleNamespace

from executing import Source
from executing.executing import is_ipython_cell_code, attr_names_match

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


def test_attr_names_match():
    assert attr_names_match("foo", "foo")

    assert not attr_names_match("foo", "_foo")
    assert not attr_names_match("foo", "__foo")
    assert not attr_names_match("_foo", "foo")
    assert not attr_names_match("__foo", "foo")

    assert attr_names_match("__foo", "_Class__foo")
    assert not attr_names_match("_Class__foo", "__foo")
    assert not attr_names_match("__foo", "Class__foo")
    assert not attr_names_match("__foo", "_Class_foo")


def test_source_reload(tmpdir):
    path = str(tmpdir.join('foo.py'))
    with open(path, "w") as f:
        f.write("1\n")

    # Initial sanity check.
    source = Source.for_filename(path)
    assert source.text == "1\n"

    # Wait a little before changing the file so that the mtime is different
    # so that linecache.checkcache() notices.
    sleep(0.01)
    with open(path, "w") as f:
        f.write("2\n")
    source = Source.for_filename(path)
    assert source.text == "2\n"
