"""Memory retained or allocated by Source and Source.executing()."""

from __future__ import annotations

import gc
import tracemalloc
from types import CodeType

from executing import Source

from ._fixtures import FunctionInLargeFile, clear_lookup_caches

FUNCTION_COUNT = 512
FILENAME = "<asv-memory-fixture>"
SOURCE_LINES = tuple(
    line
    for index in range(FUNCTION_COUNT)
    for line in (
        f"def function_{index:04d}(value):\n",
        "    result = value + 1\n",
        "    return helper(result)\n",
        "\n",
    )
)
TARGET_LINE = (FUNCTION_COUNT - 1) * 4 + 3


def _target_code() -> CodeType:
    module = compile("".join(SOURCE_LINES), FILENAME, "exec")
    name = f"function_{FUNCTION_COUNT - 1:04d}"
    return next(
        constant
        for constant in module.co_consts
        if isinstance(constant, CodeType) and constant.co_name == name
    )


TARGET_CODE = _target_code()


class _SourceMemory:
    params = ["parsed", "lines", "statements", "qualnames"]
    param_names = ["state"]

    @staticmethod
    def _make_source(state: str) -> Source:
        source = Source(FILENAME, SOURCE_LINES)
        if state == "parsed":
            pass
        elif state == "lines":
            source.lines
        elif state == "statements":
            source.statements_at_line(TARGET_LINE)
        elif state == "qualnames":
            source.code_qualname(TARGET_CODE)
        else:
            raise ValueError(state)
        return source


class SourceAllocationMemory(_SourceMemory):
    unit = "bytes"

    def _measure(self, state):
        clear_lookup_caches(Source)
        gc.collect()
        tracemalloc.start()
        source = self._make_source(state)
        retained, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        clear_lookup_caches(Source)
        del source
        return retained, peak

    def track_retained(self, state):
        return self._measure(state)[0]

    def track_peak(self, state):
        return self._measure(state)[1]


class SourcePeakMemory(_SourceMemory):
    def peakmem_first_use(self, state):
        self._make_source(state)


class FunctionInLargeFileMemory:
    unit = "bytes"

    def track_retained_after_lookup(self):
        fixture = FunctionInLargeFile()
        trace = fixture.traceback()

        class BenchmarkSource(Source):
            pass

        clear_lookup_caches(BenchmarkSource)
        gc.collect()
        tracemalloc.start()
        BenchmarkSource.executing(trace)
        retained = tracemalloc.get_traced_memory()[0]
        tracemalloc.stop()
        clear_lookup_caches(BenchmarkSource)
        return retained
