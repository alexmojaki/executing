import inspect
import linecache
import os
import sys
import inspect
import ast
from time import sleep

import pytest
from littleutils import SimpleNamespace

from executing import Source, NotOneValueFound
from executing.executing import is_ipython_cell_code, attr_names_match, KnownIssue
import executing.executing

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
    except (KnownIssue,NotOneValueFound):
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


def test_source_file_text_change(tmpdir):
    # Check that Source.for_filename notices changes in file contents
    # (assuming that linecache can notice)

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
    # Test that manually putting lines in linecache
    # under fake filenames works, and the linecache entries aren't removed.
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
    frame = inspect.currentframe()

    executing.executing.TESTING = True  # this is already the case in all other tests
    # Sanity check that this operation usually raises an exception.
    # This actually depends on executing not working in the presence of pytest.
    with pytest.raises((NotOneValueFound, KnownIssue)):
        assert Source.executing(frame).node is None

    # By contrast, TESTING is usually false when executing is used in real code.
    # In that case, the exception is caught and the result is None.
    executing.executing.TESTING = False
    try:
        assert Source.executing(frame).node is None
    finally:
        executing.executing.TESTING = True


def test_bad_linecache():
    # Test graceful failure when linecache contains source lines that don't match
    # the real code being executed.
    fake_text = "foo bar baz"  # invalid syntax, so source.tree is None
    text = """
frame = inspect.currentframe()
ex = Source.executing(frame)
"""
    filename = "<test_bad_linecache>"
    code = compile(text, filename, "exec")
    linecache.cache[filename] = (len(fake_text), 0, fake_text.splitlines(True), filename)
    globs = dict(globals())
    exec(code, globs)
    ex = globs["ex"]
    frame = globs["frame"]
    assert ex.node is None
    assert ex.statements is None
    assert ex.decorator is None
    assert ex.frame is frame
    assert ex.source.tree is None
    assert ex.source.text == fake_text
