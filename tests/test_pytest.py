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
from executing.executing import is_ipython_cell_code, attr_names_match
import executing.executing

from executing._exceptions import KnownIssue

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


if sys.version_info >= (3, 11):
    from executing._position_node_finder import mangled_name
    from textwrap import indent
    import dis

    def test_mangled_name():
        def result(*code_levels):
            code = ""
            for i, level in enumerate(code_levels):
                code += indent(level, "    " * i) + "\n"

            tree = ast.parse(code)

            for parent in ast.walk(tree):
                for child in ast.iter_child_nodes(parent):
                    child.parent = parent

            tree_names = {
                mangled_name(n)
                for n in ast.walk(tree)
                if isinstance(
                    n,
                    (
                        ast.Name,
                        ast.Attribute,
                        ast.alias,
                        ast.FunctionDef,
                        ast.ClassDef,
                        ast.AsyncFunctionDef,
                        ast.ExceptHandler,
                    ),
                )
            }

            def collect_names(code):
                for instruction in dis.get_instructions(code):
                    if instruction.opname in (
                        "STORE_NAME",
                        "LOAD_NAME",
                        "LOAD_GLOBAL",
                        "STORE_FAST",
                        "LOAD_FAST",
                        "LOAD_ATTR",
                        "STORE_ATTR",
                    ):
                        # TODO: "IMPORT_FROM" gets also mangled but is currently not handled by executing
                        #
                        # class Test:
                        #     from __mangle11c.__suc11c import __submodule11c as __subc11
                        # IMPORT_FROM(_Test__submodule11c)
                        # STORE_NAME(_Test__subc11)

                        name = instruction.argval
                        if name in ("__module__", "__qualname__", "__name__"):
                            continue

                        yield name

                for const in code.co_consts:
                    if isinstance(const, type(code)):
                        for name in collect_names(const):
                            yield name

            code_names = set(collect_names(compile(tree, "<code>", "exec")))

            assert code_names == tree_names

            return tree_names

        code = "from __mangle11c.__suc11c import __submodule11c as __subc11"

        assert result(code) == {"__subc11"}

        assert result("class Test:", code) == {"Test", "_Test__subc11"}

        assert result("class Test:", "def func():", code) == {
            "Test",
            "func",
            "_Test__subc11",
        }

        code = """
import __mangled1.submodule1
import __mangled2.__submodule2
import __mangled3.submodule3 as __sub3
import __mangled4.__submodule4 as __sub4
import __mangled5.__submodule5 as sub5
from __mangled6 import submodule6
from __mangle7.sub7 import submodule7
from __mangle8.__sub8 import submodule8
from __mangle9 import submodule9
from __mangle10.sub10 import submodule10
from __mangle11.__sub11 import submodule11
from __mangled6b import __submodule6b
from __mangle7b.sub7b import __submodule7b
from __mangle8b.__sub8b import __submodule8b
from __mangle9b import __submodule9b
from __mangle10b.sub10b import __submodule10b
from __mangle11b.__sub11b import __submodule11b
from __mangled6c import __submodule6c as __subc6
from __mangle7c.suc7c import __submodule7c as __subc7
from __mangle8c.__suc8c import __submodule8c as __subc8
from __mangle9c import __submodule9c as __subc9
from __mangle10c.suc10c import __submodule10c as __subc10
from __mangle11c.__suc11c import __submodule11c as __subc11
"""

        assert result("class Test:", "def func():", code) == {
            "Test",
            "_Test__mangled1",
            "_Test__mangled2",
            "_Test__sub3",
            "_Test__sub4",
            "_Test__subc10",
            "_Test__subc11",
            "_Test__subc6",
            "_Test__subc7",
            "_Test__subc8",
            "_Test__subc9",
            "_Test__submodule10b",
            "_Test__submodule11b",
            "_Test__submodule6b",
            "_Test__submodule7b",
            "_Test__submodule8b",
            "_Test__submodule9b",
            "func",
            "sub5",
            "submodule10",
            "submodule11",
            "submodule6",
            "submodule7",
            "submodule8",
            "submodule9",
        }

        code = """
__mangled_var=3
__not_mangled__=5
normal_var=6

q.__attribute

try:
    pass
except TypeError as __exception:
    pass

for __var in [1]:
    pass
"""
        assert result("class Test:", "def func():", code) == {
            "Test",
            "TypeError",
            "_Test__attribute",
            "_Test__exception",
            "_Test__mangled_var",
            "_Test__var",
            "__not_mangled__",
            "func",
            "normal_var",
            "q",
        }

        # different context

        assert result("class Test:", "def func():", "e.__a=5") == {
            "Test",
            "func",
            "_Test__a",
            "e",
        }

        assert result("class __Test:", "def func():", "e.__a=5") == {
            "__Test",
            "func",
            "_Test__a",
            "e",
        }

        assert result("class __Test:", "e.__a=5") == {
            "__Test",
            "_Test__a",
            "e",
        }

        assert result("class __Test_:", "def func():", "e.__a=5") == {
            "__Test_",
            "func",
            "_Test___a",
            "e",
        }

        assert result("class ___Test_:", "def func():", "e.__a=5") == {
            "___Test_",
            "func",
            "_Test___a",
            "e",
        }


        assert result("class __Testa:","class __Testb:" ,"e.__a=5") == {
            "__Testa",
            "_Testa__Testb",
            "_Testb__a",
            "e",
        }
