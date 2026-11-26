import ast
import dis
import inspect

from executing import Source, _utils


def test_three_locations_in_one_function_share_disassembly(monkeypatch):
    def run():
        frame = inspect.currentframe()
        first = Source.executing(frame)
        second = Source.executing(frame)
        third = Source.executing(frame)
        return first, second, third

    disassemblies = 0
    original_get_instructions = dis.get_instructions

    def get_instructions(code, *args, **kwargs):
        nonlocal disassemblies
        # Sentinel lookups also disassemble newly compiled candidate code.
        if code is run.__code__:
            disassemblies += 1
        return original_get_instructions(code, *args, **kwargs)

    monkeypatch.setattr(dis, "get_instructions", get_instructions)
    monkeypatch.setattr(_utils, "_get_instructions", get_instructions)

    results = run()

    assert all(isinstance(result.node, ast.Call) for result in results)
    assert len({result.node.lineno for result in results}) == 3
    assert disassemblies == 1
