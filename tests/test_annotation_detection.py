import ast
import dis
import sys
import types

import pytest

from executing import Source


pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 14), reason="requires compiler-generated annotation functions"
)


def nested_codes(code):
    for const in code.co_consts:
        if isinstance(const, types.CodeType):
            yield const
            yield from nested_codes(const)


@pytest.mark.parametrize(
    "source, name",
    [
        ("x: int", "__annotate__"),
        ("def f(x: int) -> str: pass", "__annotate__"),
        ("class C:\n    x: int", "__annotate__"),
        ("type Alias = list[int]", "Alias"),
        ("def f[T: int](x: T): pass", "T"),
        ("def f[T: int](x: T): pass", "__annotate__"),
    ],
)
def test_annotation_header_ends_at_body(source, name):
    from executing._position_node_finder import PositionNodeFinder

    code = next(
        code for code in nested_codes(compile(source, "<test>", "exec"))
        if code.co_name == name
    )
    instructions = list(dis.get_instructions(code))
    finder = PositionNodeFinder.__new__(PositionNodeFinder)
    finder.frame = types.SimpleNamespace(f_code=code)
    finder.bc_dict = {inst.offset: inst for inst in instructions}

    end = finder.annotation_header_end()
    raise_index = next(
        i for i, inst in enumerate(instructions) if inst.opname == "RAISE_VARARGS"
    )
    assert end == instructions[raise_index + 1].offset


@pytest.mark.parametrize(
    "source",
    [
        "def callback(number):\n    0 if number == 0 else 0",
        "def callback(format, /):\n    0 if format == 0 else 0",
        "def callback(format, /):\n    0 if format > 2 else 0",
        "def callback(format, /):\n    if format == 2: raise NotImplementedError",
        "def callback(format, /):\n    if format > 1: raise NotImplementedError",
        "def callback(format, /):\n    if format > 2: raise ValueError",
    ],
)
def test_ordinary_comparison_is_not_annotation_code(tmp_path, source, monkeypatch):
    import executing.executing

    monkeypatch.setattr(executing.executing, "TESTING", True)
    filename = tmp_path / "comparison.py"
    filename.write_text(source)
    code = next(nested_codes(compile(source, str(filename), "exec")))
    comparison = next(
        inst for inst in dis.get_instructions(code) if inst.opname == "COMPARE_OP"
    )
    frame = types.SimpleNamespace(
        f_code=code,
        f_lasti=comparison.offset,
        f_lineno=comparison.positions.lineno,
        f_globals={},
    )
    assert isinstance(Source.executing(frame).node, ast.Compare)
