# executing

[![Build Status](https://travis-ci.org/alexmojaki/executing.svg?branch=master)](https://travis-ci.org/alexmojaki/executing) [![Coverage Status](https://coveralls.io/repos/github/alexmojaki/executing/badge.svg?branch=master)](https://coveralls.io/github/alexmojaki/executing?branch=master) [![Supports Python versions 2.7 and 3.4+, including PyPy](https://img.shields.io/pypi/pyversions/executing.svg)](https://pypi.python.org/pypi/executing)

This mini-package lets you get information about what a frame is currently doing, particularly the AST node being executed. Typical usage:

    import executing

    node = executing.Source.executing(frame).node
    # node will be an AST node or None

Currently it only works for function calls and corresponding `ast.Call` nodes, but the plan is to expand to as many operations as possible. It can find the call node in almost any situation where the source code is available (obtained from `linecache`). The only known exception is if you have two very similar looking list/dict/set comprehensions, generator expressions, or lambdas on the same line.

This package can be installed with `pip install executing`, or if you don't like that you can just copy the file `executing.py`, there are no dependencies (but of course you won't get updates).

The `node` returned in the snippet above will always be the same instance
for multiple calls with frames at the same point of execution.

Everything goes through the `Source` class. Only one instance of the class is created for each filename. Subclassing it to add more attributes on creation or methods is recommended. The classmethods such as `executing` will respect this. See the source code and docstrings for more detail.

You can also get the `__qualname__` of the function being executed, with either:

    executing.Source.executing(frame).code_qualname()

or:

    executing.Source.for_frame(frame).code_qualname(frame.f_code)

To get the source code of a node, separately install the [`asttokens`](https://github.com/gristlabs/asttokens) library, then obtain an `ASTTokens` object:

    executing.Source.executing(frame).source.asttokens()

or:

    executing.Source.for_frame(frame).asttokens()

or use one of the convenience methods:

    executing.Source.executing(frame).get_text()
    executing.Source.executing(frame).get_text_range()
