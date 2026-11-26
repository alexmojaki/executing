# Development workflows & tools

## Performance benchmarks

Run benchmarks from the repository root using `uv`. Enable their dependencies
with `--group benchmarks`; the tools require Python 3.12+, which `uv` selects
automatically. Normal development commands do not require this group.

To validate the suite and smoke-test the working tree:

```sh
uv run --locked --group benchmarks asv machine --yes
uv run --locked --group benchmarks asv check -E existing
uv run --locked --group benchmarks asv run -E existing --quick --show-stderr --dry-run
```

Use `--quick` only for smoke checks, not for reliable timing comparisons.
Measured comparisons build committed revisions in separate environments.

### Comparing revisions

To benchmark the merge base and every subsequent commit on the current branch,
then generate a report:

```sh
./benchmarks/run_branch_benchmarks.sh
uv run --locked --group benchmarks asv preview
```

The script installs missing benchmark interpreters. Set `BASE_BRANCH` when
comparing against a branch other than `master`. Additional arguments are passed
to `asv run`: use `--bench REGEX` to select benchmarks, `--quick` for a smoke
check, or `--skip-existing-successful` to fill in missing results.

The `pythons` list in `asv.conf.json` defines the interpreter matrix for local
runs and PR benchmarks. To compare only the merge base and current commit using
a specific interpreter:

```sh
uv run --locked --group benchmarks --python 3.14 asv continuous \
  "$(git merge-base master HEAD)" HEAD --python 3.14 --show-stderr
uv run --locked --group benchmarks asv publish
uv run --locked --group benchmarks asv preview
```

The first `--python` selects the interpreter running the tools; ASV's separate
`--python` selects the benchmark interpreter. Omitting ASV's option uses the
configured matrix. Environments, results, and generated reports live in the
ignored `.asv/` directory.

### What the benchmarks measure

The suite in `benchmarks/asv_benchmarks/` covers calls, binary operations,
attribute access, multiline calls, calls in large functions, and small functions
in large source files. Timings include `Source.executing()` and access to
`.node`, `.statements`, both together, `.text()`, `.text_range()`, or
`.code_qualname()`.

| Benchmark | Cache state | Reported timing |
| --- | --- | --- |
| `Cached.time_1000_lookups` | Execution result and requested metadata cached | Total for 1,000 lookups |
| `ExecutionCacheMiss.time_lookup` | Parsed source and instruction metadata retained; execution result uncached | One lookup |
| `ColdLookup.time_lookup` | Source and lookup caches cleared | One lookup, including source loading and parsing |

Cold lookups do not clear the operating system's file cache. Cached batch times
should not be compared directly with the single-lookup times.

Memory benchmarks report retained and peak Python allocations for `Source`
construction and selected first accesses, plus process-level peak memory.
Allocation totals include constructing the `Source`, rather than only the
additional cost of accessing a property. Run only memory benchmarks with:

```sh
uv run --locked --group benchmarks asv run --bench memory
```

For adding or changing benchmarks, see the
[ASV benchmark guide](https://asv.readthedocs.io/en/stable/writing_benchmarks.html).

### Pull request reports

PR benchmarks compare the merge base with the PR head on the same runner for
each configured Python version. Comments label the comparison `Merge base` →
`PR`. To include interactions with newer target-branch changes, update the PR
branch first.

Results appear as one comparison comment per Python version, including for fork
PRs. The comment workflow must be present on the default branch to run. Results
are informational: timing changes do not fail CI or convert PRs to drafts.
Hosted runners can be noisy, so confirm small timing differences locally.

## Checking source files

executing can check arbitrary Python source files:

- files in `tests/small_samples` are checked by default  
- files in `tests/samples` are checked if the `EXECUTING_SLOW_TESTS=1` is set 

run slow tests in parallel:
~~~ sh
env EXECUTING_SLOW_TESTS=1 tox -p
~~~

pytest parmeters can be passed to tox.

~~~ sh
env EXECUTING_SLOW_TESTS=1 tox -e py311 -- --sw
~~~


## Coverage

After installing the test dependencies with `pip install -e '.[tests]'`, run
coverage from the repository root:

```sh
export COVERAGE_PROCESS_START="$PWD/pyproject.toml"
EXECUTING_SLOW_TESTS=1 coverage run -m pytest tests
coverage combine
coverage report -m
coverage html
```

Open `htmlcov/index.html` for the local report. The shared configuration measures
the whole `executing` package, including modules not imported on the current
Python version, without including test samples or dependencies. The subprocess
startup configuration and `coverage combine` include measurements from child
processes as well. Run `coverage erase` before starting a fresh measurement if
there is coverage data left over from an earlier run.

## generate_small_sample

`tox -e genererate_small_sample` can be used to:

1. find python source code which triggers a bug in executing
2. minimize this source code
3. stores this samples in `tests/small_samples`

Usage:

minimize failures in `tests/samples` 
~~~ sh
tox -e generate_small_sample-py311 
~~~

search other project for potential problems 
~~~ sh
tox -e generate_small_sample-py311 -- ~/path/to/python-3.11.0/
~~~

## mutmut

[mutmut](https://mutmut.readthedocs.io/en/latest/) can be used to mutation testing

The weak points in the tests which are discovered by mutmut are normally fixed by developer (creating new test cases).

But "tox -e mutmut" combines `generate_small_sample` and mutmut.
Tests are generated automatically for issues which are discovered by mutmut.

Usage:
```
tox -e mutmut
```

You should have a clean git working directory, because mutmut changes files.

## pre-commit (ruff)

Run ruff checks/formatting with pre-commit:

```sh
pre-commit run --all-files
```

Install the hook locally:

```sh
pre-commit install
```




