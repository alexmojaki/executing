import inspect
import linecache
import os
import sys
from time import sleep

import pytest
from littleutils import SimpleNamespace

from executing import Source, NotOneValueFound
from executing.executing import is_ipython_cell_code, attr_names_match
import executing.executing

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


def test_manual_linecache():
    check_manual_linecache(os.path.join("fake", "path", "to", "foo.py"))
    check_manual_linecache("<my_custom_filename>")


def check_manual_linecache(filename):
    text = "foo\nbar\n"
    lines = text.splitlines(True)
    assert lines == ["foo\n", "bar\n"]

    entry = (len(text), 0, lines, filename)
    linecache.cache[filename] = entry

    # sanity check
    assert linecache.cache[filename] == entry
    assert linecache.getlines(filename) == lines

    # checkcache normally removes the entry because the filename doesn't exist
    linecache.checkcache(filename)
    assert filename not in linecache.cache
    assert linecache.getlines(filename) == []

    # Source.for_filename uses checkcache but makes sure the entry isn't removed
    linecache.cache[filename] = entry
    source = Source.for_filename(filename)
    assert linecache.cache[filename] == entry
    assert source.text == text


def test_exception_catching():
    executing.executing.TESTING = True
    with pytest.raises(NotOneValueFound):
        assert Source.executing(inspect.currentframe()).node is None

    executing.executing.TESTING = False
    try:
        assert Source.executing(inspect.currentframe()).node is None
    finally:
        executing.executing.TESTING = True
