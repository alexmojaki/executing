# Development workflows & tools

executing can check arbitrary python source files:

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




