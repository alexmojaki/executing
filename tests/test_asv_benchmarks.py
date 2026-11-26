"""Check benchmark workloads through ASV entry points and executing's API."""

import ast

import pytest

from benchmarks.asv_benchmarks.executing import Cached, ColdLookup, ExecutionCacheMiss
from executing import Source
from executing import executing as library


@pytest.fixture
def observations(monkeypatch):
    events = {"lookups": [], "accesses": [], "source_loads": [], "node_searches": []}
    original_executing = Source.executing.__func__
    original_init = Source.__init__
    original_finder = library.NodeFinder

    class ObservedResult:
        """Observe the consumer without changing the real lookup or its caches."""

        def __init__(self, result):
            self.result = result

        def __getattr__(self, name):
            value = getattr(self.result, name)
            if callable(value):

                def call(*args, **kwargs):
                    events["accesses"].append(name)
                    return value(*args, **kwargs)

                return call
            events["accesses"].append(name)
            return value

    def executing(cls, frame_or_tb):
        result = original_executing(cls, frame_or_tb)
        events["lookups"].append(result)
        return ObservedResult(result)

    def init(self, *args, **kwargs):
        events["source_loads"].append(None)
        original_init(self, *args, **kwargs)

    def find_node(*args, **kwargs):
        events["node_searches"].append(None)
        return original_finder(*args, **kwargs)

    monkeypatch.setattr(Source, "executing", classmethod(executing))
    monkeypatch.setattr(Source, "__init__", init)
    monkeypatch.setattr(library, "NodeFinder", find_node)
    return events


@pytest.mark.parametrize(
    "benchmark_cls,method,lookup_count,source_loads,node_searches",
    [
        (Cached, "time_1000_lookups", 1_000, 0, 0),
        (ExecutionCacheMiss, "time_lookup", 1, 0, 1),
        (ColdLookup, "time_lookup", 1, 1, 1),
    ],
)
@pytest.mark.parametrize(
    "usage,accesses",
    [
        ("node", ["node"]),
        ("statements", ["statements"]),
        ("node_and_statements", ["node", "statements"]),
        ("text", ["text"]),
        ("text_range", ["text_range"]),
        ("code_qualname", ["code_qualname"]),
    ],
)
def test_samples_perform_requested_lookup_in_the_intended_cache_state(
    benchmark_cls,
    method,
    lookup_count,
    source_loads,
    node_searches,
    usage,
    accesses,
    observations,
):
    benchmark = benchmark_cls()
    for _ in range(3):
        benchmark.setup("call", usage)
        for events in observations.values():
            events.clear()

        getattr(benchmark, method)("call", usage)

        assert len(observations["lookups"]) == lookup_count
        assert observations["accesses"] == accesses * lookup_count
        assert len(observations["source_loads"]) == source_loads
        assert len(observations["node_searches"]) == node_searches
        assert all(
            isinstance(result.node, ast.Call) for result in observations["lookups"]
        )


@pytest.mark.parametrize(
    "operation,node_type",
    [
        ("call", ast.Call),
        ("bin-op", ast.BinOp),
        ("attribute-access", ast.Attribute),
        ("call-multiline", ast.Call),
        ("call-large-function", ast.Call),
        ("function-in-large-file", ast.Call),
    ],
)
def test_lookup_scenarios_find_the_intended_operation(
    operation, node_type, observations
):
    benchmark = ColdLookup()
    benchmark.setup(operation, "node")
    observations["lookups"].clear()

    benchmark.time_lookup(operation, "node")

    assert len(observations["lookups"]) == 1
    result = observations["lookups"][0]
    assert isinstance(result.node, node_type)
    assert result.statements
    assert result.text() == ast.get_source_segment(result.source.text, result.node)
