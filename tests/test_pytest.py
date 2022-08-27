import importlib
import os
import sys
from time import sleep

from littleutils import SimpleNamespace

from executing import Source
from executing.executing import is_ipython_cell_code, attr_names_match, PY3

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


class MySource(Source):
    pass


class MySource2(MySource):
    pass


def test_source_reload(tmpdir):
    if not PY3:
        return

    from executing.executing import ReloadCacheFinder
    assert sum(isinstance(x, ReloadCacheFinder) for x in sys.meta_path) == 1

    check_source_reload(tmpdir, Source)
    check_source_reload(tmpdir, MySource)
    check_source_reload(tmpdir, MySource2)


def check_source_reload(tmpdir, SourceClass):
    from pathlib import Path

    modname = "test_tmp_module_" + SourceClass.__name__
    path = Path(str(tmpdir)) / ("%s.py" % modname)
    with path.open("w") as f:
        f.write("1\n")

    sys.path.append(str(tmpdir))
    mod = importlib.import_module(modname)
    # ReloadCacheFinder uses __file__ so it needs to be the same
    # as what we pass to Source.for_filename here.
    assert mod.__file__ == str(path)

    # Initial sanity check.
    source = SourceClass.for_filename(path)
    assert source.text == "1\n"

    # Wait a little before changing the file so that the mtime is different
    # so that linecache.checkcache() notices.
    sleep(0.01)
    with path.open("w") as f:
        f.write("2\n")
    source = SourceClass.for_filename(path)
    assert source.text == "2\n"
