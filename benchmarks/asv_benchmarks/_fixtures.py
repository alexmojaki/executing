"""Generate real traceback fixtures in independent temporary source files."""

import ast
import linecache
import sys
import weakref
from pathlib import Path
from tempfile import TemporaryDirectory

from executing import Source
from executing.executing import statement_containing_node


class Case:
    node_type = ast.Call

    def __init__(self):
        self.directory = TemporaryDirectory(prefix="executing-asv-")
        self.filename = Path(self.directory.name) / "fixture.py"
        # Older Python versions replace linecache.cache when clearing it.
        weakref.finalize(
            self,
            lambda filename: linecache.cache.pop(filename, None),
            str(self.filename),
        )
        source = self.source()
        self.filename.write_text(source, encoding="utf-8")
        namespace = {"__name__": "asv_fixture", "__file__": str(self.filename)}
        exec(compile(source, str(self.filename), "exec"), namespace)
        self.function = namespace["run"]

    def source(self):
        return (
            "def _raise_error(*args):\n"
            '    raise RuntimeError("benchmark")\n\n'
            "def run():\n" + self.body()
        )

    def body(self):
        return f"    return {self.expected_text}\n"

    def traceback(self):
        try:
            self.function()
        except Exception as exc:
            return exc.__traceback__.tb_next
        raise AssertionError("fixture did not raise")

    def make_reader(self, usage, warm, cold=False):
        trace = self.traceback()

        # Isolate caches without depending on the execution-cache key/value layout.
        class BenchmarkSource(Source):
            pass

        self.source_cls = BenchmarkSource

        result = self.source_cls.executing(trace)
        assert isinstance(result.node, self.node_type)
        assert result.statements == {result.node.parent}

        self._warm = warm
        self._cold = cold
        if not warm and not cold:
            self._source = result.source
            # Preserve eager metadata on older revisions and lazy defaults on
            # newer ones, without parsing a new Source for every sample.
            self._source_metadata = {
                name: getattr(result.source, name)
                for name in ("_asttokens", "_asttext", "_qualnames")
            }

        def node_and_statements():
            result = self.source_cls.executing(trace)
            return result.node, result.statements

        readers = {
            "node": lambda: self.source_cls.executing(trace).node,
            "statements": lambda: self.source_cls.executing(trace).statements,
            "node_and_statements": node_and_statements,
            "text": lambda: self.source_cls.executing(trace).text(),
            "text_range": lambda: self.source_cls.executing(trace).text_range(),
            "code_qualname": lambda: self.source_cls.executing(trace).code_qualname(),
        }
        read = readers[usage]
        if warm:
            value = read()
            if usage == "text":
                assert value == self.expected_text
            elif usage == "text_range":
                assert result.source.text[slice(*value)] == self.expected_text
            elif usage == "code_qualname":
                assert value == self.function.__qualname__
        self.reset()
        return read

    def reset(self):
        """Prepare another sample without regenerating code or its traceback."""
        if self._warm:
            return
        if self._cold:
            # The timed lookup reloads source text and constructs all metadata.
            clear_lookup_caches(self.source_cls)
        else:
            # Retain source and bytecode, with a fresh lookup and first-use text.
            clear_lookup_caches(self.source_cls, execution_cache_only=True)
            for name, value in self._source_metadata.items():
                setattr(self._source, name, value)


class Call(Case):
    expected_text = "_raise_error()"


class BinOp(Case):
    node_type = ast.BinOp
    expected_text = "1 / 0"


class AttributeAccess(Case):
    node_type = ast.Attribute
    expected_text = "object().missing"


class CallMultiline(Case):
    argument_count = 3_000

    @property
    def expected_text(self):
        return (
            "_raise_error(\n"
            + "".join(f"        {i},\n" for i in range(self.argument_count))
            + "    )"
        )


class CallLargeFunction(Call):
    statement_count = 1_000
    statement_width = 16
    nesting_depth = 24

    def statement(self, index):
        expression = (
            "["
            + ", ".join(
                f"abs({index + offset})" for offset in range(self.statement_width)
            )
            + "]"
        )
        for depth in range(self.nesting_depth):
            if depth % 3 == 0:
                expression = f"[{expression}, {index}]"
            elif depth % 3 == 1:
                expression = f"({expression}, {index})"
            else:
                expression = f"tuple([{expression}, {index}])"
        return f"    value = {expression}\n"

    def body(self):
        # Unroll substantial expressions to grow both bytecode and AST depth.
        return (
            "".join(self.statement(index) for index in range(self.statement_count))
            + super().body()
        )


class FunctionInLargeFile(Call):
    function_count = 1_000
    entries_per_function = 10

    def source(self):
        # Surround the small measured function with substantial unrelated ASTs.
        functions = [
            f"def function_{index}():\n    values = []\n"
            + "".join(
                f'    values.append({{"index": {index}, "entry": {entry}, '
                '"items": [item * 2 for item in range(4)]})\n'
                for entry in range(self.entries_per_function)
            )
            + "    return values\n\n"
            for index in range(self.function_count)
        ]
        functions.insert(self.function_count // 2, super().source() + "\n")
        return "".join(functions)


CASES = {
    "call": Call,
    "bin-op": BinOp,
    "attribute-access": AttributeAccess,
    "call-multiline": CallMultiline,
    "call-large-function": CallLargeFunction,
    "function-in-large-file": FunctionInLargeFile,
}


def clear_lookup_caches(source_cls, *, execution_cache_only=False):
    if not execution_cache_only:
        # Older reset helpers did not clear Python's source-text cache.
        linecache.clearcache()
    clear = getattr(source_cls, "_clear_caches", None)
    if clear is not None:
        if not execution_cache_only:
            clear()
        elif "execution_cache_only" in clear.__func__.__code__.co_varnames:
            # Full signature inspection perturbs the following short lookup timing.
            clear(execution_cache_only=True)
        else:
            # Older revisions used a shorter keyword for this reset mode.
            clear(execution_only=True)
        return

    # Historical revisions do not have Source._clear_caches().
    source_cls._class_local("__executing_cache", {}).clear()
    if execution_cache_only:
        return
    source_cls._class_local("__source_cache_with_lines", {}).clear()
    source_cls.statements_at_line.cache_clear()
    statement_containing_node.cache_clear()

    if sys.version_info >= (3, 11):
        from executing import _position_node_finder

        for name in ("_instruction_cache", "_decoder_cache"):
            instruction_cache = getattr(_position_node_finder, name, None)
            if instruction_cache is not None:
                instruction_cache.clear()
        for name in (
            "get_instructions",
            "annotation_header_end",
            "_annotation_header_end",
        ):
            cache_clear = getattr(
                getattr(_position_node_finder, name, None), "cache_clear", None
            )
            if cache_clear is not None:
                cache_clear()
