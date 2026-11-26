import gc
import linecache
import weakref

import pytest

from executing import Source


def traceback():
    try:
        1 / 0
    except ZeroDivisionError as exc:
        return exc.__traceback__


@pytest.fixture
def source_cls():
    class LocalSource(Source):
        pass

    yield LocalSource
    LocalSource._clear_caches()


def test_full_reset_rebuilds_lookups_and_keeps_existing_results_usable(source_cls):
    trace = traceback()
    first = source_cls.executing(trace)
    text = first.text()
    text_range = first.text_range()
    qualname = first.code_qualname()

    source_cls._clear_caches()
    rebuilt = source_cls.executing(trace)

    assert rebuilt.source is not first.source
    assert rebuilt.node is not first.node
    assert rebuilt.text() == first.text() == text == "1 / 0"
    assert rebuilt.text_range() == first.text_range() == text_range
    assert rebuilt.code_qualname() == first.code_qualname() == qualname


def test_full_reset_releases_objects_retained_only_by_caches(source_cls, tmp_path):
    filename = tmp_path / "lookup.py"
    text = "def run():\n    1 / 0\n"
    filename.write_text(text)

    def populate_caches():
        namespace = {}
        exec(compile(text, str(filename), "exec"), namespace)
        try:
            namespace["run"]()
        except ZeroDivisionError as exc:
            result = source_cls.executing(exc.__traceback__.tb_next)
        assert result.text() == "1 / 0"
        return (
            weakref.ref(result.source),
            weakref.ref(result.frame.f_code),
        )

    references = populate_caches()
    gc.collect()
    assert all(reference() is not None for reference in references)

    source_cls._clear_caches()
    gc.collect()

    assert all(reference() is None for reference in references)


def test_execution_only_reset_repeats_source_lookup(source_cls, monkeypatch):
    trace = traceback()
    source_cls.executing(trace)
    original = source_cls.for_frame
    frames = []

    def for_frame(cls, frame):
        frames.append(frame)
        return original(frame)

    monkeypatch.setattr(source_cls, "for_frame", classmethod(for_frame))
    source_cls.executing(trace)
    assert not frames

    source_cls._clear_caches(execution_cache_only=True)
    source_cls.executing(trace)

    assert frames == [trace.tb_frame]


def test_execution_only_reset_preserves_source_and_initialized_metadata(source_cls):
    trace = traceback()
    first = source_cls.executing(trace)
    asttext = first.source.asttext()
    asttokens = first.source.asttokens()
    text = first.text()
    text_range = first.text_range()
    qualname = first.code_qualname()

    source_cls._clear_caches(execution_cache_only=True)
    rebuilt = source_cls.executing(trace)

    assert rebuilt.source is first.source
    assert rebuilt.node is first.node
    assert rebuilt.source.asttext() is asttext
    assert rebuilt.source.asttokens() is asttokens
    assert rebuilt.text() == text
    assert rebuilt.text_range() == text_range
    assert rebuilt.code_qualname() == qualname


@pytest.mark.parametrize("execution_cache_only", [False, True])
def test_reset_preserves_other_subclasses_source_cache(
    source_cls, execution_cache_only
):
    class OtherSource(Source):
        pass

    trace = traceback()
    source_cls.executing(trace)
    other = OtherSource.executing(trace)

    source_cls._clear_caches(execution_cache_only=execution_cache_only)

    assert OtherSource.for_frame(trace.tb_frame) is other.source
    assert OtherSource.executing(trace).source is other.source


@pytest.mark.parametrize("execution_cache_only", [False, True])
def test_reset_controls_python_source_text_cache(
    source_cls, tmp_path, execution_cache_only
):
    filename = tmp_path / "source.py"
    filename.write_text("before\n")
    assert linecache.getline(str(filename), 1) == "before\n"
    filename.write_text("after\n")

    source_cls._clear_caches(execution_cache_only=execution_cache_only)

    expected = "before\n" if execution_cache_only else "after\n"
    assert linecache.getline(str(filename), 1) == expected
