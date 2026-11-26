"""Cross product of executing operations and consumers of Executing results."""

from ._fixtures import CASES


class _Matrix:
    params = [
        list(CASES),
        [
            "node",
            "statements",
            "node_and_statements",
            "text",
            "text_range",
            "code_qualname",
        ],
    ]
    param_names = ["operation", "usage"]
    rounds = 2
    repeat = 25
    # Keep headroom for expensive operations on older revisions/interpreters.
    timeout = 300

    def _setup_reader(self, operation, usage, warm=False, cold=False):
        params = (operation, usage)
        if getattr(self, "_reader_params", None) != params:
            self.fixture = CASES[operation]()
            self.read = self.fixture.make_reader(usage, warm=warm, cold=cold)
            self._reader_params = params
        else:
            self.fixture.reset()


class Cached(_Matrix):
    # Time a batch so per-call setup isolation does not measure each tiny hit.
    # ASV reports the total time for 1,000 lookups, not the time per lookup.
    number = 1
    repeat = 5

    def setup(self, operation, usage):
        self._setup_reader(operation, usage, warm=True)

    def time_1000_lookups(self, operation, usage):
        read = self.read
        for _ in range(1_000):
            read()


class ExecutionCacheMiss(_Matrix):
    # Never batch cache misses: a second call would become a cache hit.
    number = 1
    warmup_time = 0

    def setup(self, operation, usage):
        # Short misses need more samples to outlast the initial timing transient.
        # See the sampling guidance in development.md.
        self.repeat = 25
        if operation == "call-large-function":
            self.repeat = 5 if usage in ("text", "text_range") else 10
        elif operation == "function-in-large-file":
            self.repeat = 15 if usage in ("text", "text_range") else 20
        elif operation == "call-multiline" and usage in ("text", "text_range"):
            self.repeat = 10
        self._setup_reader(operation, usage)

    def time_lookup(self, operation, usage):
        self.read()


class ColdLookup(_Matrix):
    # The timed call reloads source text and constructs all executing metadata.
    # Never batch: a second call would become a cache hit.
    number = 1
    warmup_time = 0

    def setup(self, operation, usage):
        # Include source-file loading after a full reset of linecache.
        self.repeat = 25
        if operation in ("call-large-function", "function-in-large-file"):
            self.repeat = 5
        elif operation == "call-multiline":
            self.repeat = 10
        self._setup_reader(operation, usage, cold=True)

    def time_lookup(self, operation, usage):
        self.read()
