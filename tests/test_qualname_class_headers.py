import sys
import textwrap

import pytest

from executing import Source


@pytest.mark.parametrize("scope", ["module", "function", "class"])
@pytest.mark.parametrize(
    "case",
    [
        "decorator",
        "base",
        "metaclass",
        "nested_class",
        "class_body",
        "function_decorator",
        "function_default",
    ],
)
def test_class_header_qualnames(tmp_path, scope, case):
    header = """
functions = {}
def remember(name, func):
    functions[name] = func
    return func
"""
    definitions = """
@remember("decorator", lambda cls: cls)
class Decorated:
    pass
class Based(remember("base", lambda: object)()):
    pass
class Meta(metaclass=remember("metaclass", lambda name, bases, attrs: type(name, bases, attrs))):
    pass
class Outer:
    @remember("nested_class", lambda cls: cls)
    class Inner:
        pass
    member = remember("class_body", lambda: None)
@remember("function_decorator", lambda func: func)
def decorated(arg=remember("function_default", lambda: None)):
    pass
"""
    if scope == "module":
        source_text = header + definitions
    elif scope == "function":
        source_text = header + "\ndef make():\n" + textwrap.indent(definitions, "    ")
        source_text += "\nmake()\n"
    else:
        source_text = (
            header + "\nclass Enclosing:\n" + textwrap.indent(definitions, "    ")
        )

    path = tmp_path / "class_headers.py"
    path.write_text(source_text, encoding="utf-8")
    namespace = {}
    exec(compile(source_text, str(path), "exec"), namespace)
    func = namespace["functions"][case]
    source = Source.for_filename(path)
    assert source.code_qualname(func.__code__) == func.__qualname__


@pytest.mark.skipif(
    sys.version_info < (3, 12), reason="type parameter syntax requires 3.12"
)
@pytest.mark.parametrize("case", ["decorator", "base", "metaclass"])
def test_generic_class_header_qualnames(tmp_path, case):
    source_text = """
functions = {}
def remember(name, func):
    functions[name] = func
    return func
class Base:
    pass
@remember("decorator", lambda cls: cls)
class Generic[T](remember("base", lambda: Base)(), metaclass=remember("metaclass", lambda name, bases, attrs: type(name, bases, attrs))):
    pass
"""
    path = tmp_path / "generic_class_headers.py"
    path.write_text(source_text, encoding="utf-8")
    namespace = {}
    exec(compile(source_text, str(path), "exec"), namespace)
    func = namespace["functions"][case]
    assert Source.for_filename(path).code_qualname(func.__code__) == func.__qualname__
