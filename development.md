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




