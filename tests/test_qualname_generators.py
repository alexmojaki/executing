import textwrap

import pytest

from executing import Source


@pytest.mark.parametrize("scope", ["module", "function", "class"])
@pytest.mark.parametrize(
    "expression",
    [
        "list((lambda: i) for i in range(1))",
        "list(i for i in [(lambda: None)])",
        "list(i for i in range(1) if remember(lambda: None))",
        "list(j for i in range(1) for j in [(lambda: None)])",
        "list(j for i in range(1) for j in ((lambda: k) for k in range(1)))",
        "list((lambda: (lambda: None)) for i in range(1))",
        "[f for f in ((lambda: None) for i in range(1))]",
        "list(f for f in ((lambda: None) for i in range(1)))",
    ],
)
def test_generator_lambda_qualnames(tmp_path, scope, expression):
    definitions = "functions = " + expression + "\n"
    header = "captured = []\ndef remember(func):\n    captured.append(func)\n    return True\n"
    if scope == "module":
        source_text = (
            header
            + definitions
            + "captured.extend(f for f in functions if callable(f))\n"
        )
    elif scope == "function":
        source_text = (
            header + "def enclosing():\n" + textwrap.indent(definitions, "    ")
        )
        source_text += "    return functions\ncaptured.extend(f for f in enclosing() if callable(f))\n"
    else:
        source_text = (
            header + "class Enclosing:\n" + textwrap.indent(definitions, "    ")
        )
        source_text += (
            "captured.extend(f for f in Enclosing.functions if callable(f))\n"
        )
    path = tmp_path / "generator_lambdas.py"
    path.write_text(source_text, encoding="utf-8")
    namespace = {}
    exec(compile(source_text, str(path), "exec"), namespace)
    source = Source.for_filename(path)
    assert namespace["captured"]
    for func in namespace["captured"]:
        assert source.code_qualname(func.__code__) == func.__qualname__


@pytest.mark.parametrize("scope", ["module", "function", "class"])
def test_nested_lambda_in_generator_qualnames(tmp_path, scope):
    definitions = """functions = list(
    (lambda:
        (lambda: None))
    for i in range(1)
)
"""
    if scope == "module":
        source_text = definitions + "outer = functions[0]\n"
    elif scope == "function":
        source_text = "def enclosing():\n" + textwrap.indent(definitions, "    ")
        source_text += "    return functions\nouter = enclosing()[0]\n"
    else:
        source_text = "class Enclosing:\n" + textwrap.indent(definitions, "    ")
        source_text += "outer = Enclosing.functions[0]\n"
    source_text += "inner = outer()\n"
    path = tmp_path / "nested_generator_lambdas.py"
    path.write_text(source_text, encoding="utf-8")
    namespace = {}
    exec(compile(source_text, str(path), "exec"), namespace)
    source = Source.for_filename(path)
    for name in ("outer", "inner"):
        func = namespace[name]
        assert source.code_qualname(func.__code__) == func.__qualname__
