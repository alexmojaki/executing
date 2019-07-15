# executing

[![Build Status](https://travis-ci.org/alexmojaki/executing.svg?branch=master)](https://travis-ci.org/alexmojaki/executing) [![Coverage Status](https://coveralls.io/repos/github/alexmojaki/executing/badge.svg?branch=master)](https://coveralls.io/github/alexmojaki/executing?branch=master) [![Supports Python versions 2.7 and 3.4+, including PyPy](https://img.shields.io/pypi/pyversions/executing.svg)](https://pypi.python.org/pypi/executing)

This mini-package lets you get information about what a frame is currently doing, particularly the AST node being executed.
 
## Usage

### Getting the AST node

    import executing

    node = executing.Source.executing(frame).node

Then `node` will be an AST node (from the `ast` standard library module) or None if the node couldn't be identified (which may happen often and should always be checked).

`node` will always be the same instance for multiple calls with frames at the same point of execution.

### Getting the source code of the node

For this you will need to separately install the [`asttokens`](https://github.com/gristlabs/asttokens) library, then obtain an `ASTTokens` object:

    executing.Source.executing(frame).source.asttokens()

or:

    executing.Source.for_frame(frame).asttokens()

or use one of the convenience methods:

    executing.Source.executing(frame).get_text()
    executing.Source.executing(frame).get_text_range()

### Getting the `__qualname__` of the current function

    executing.Source.executing(frame).code_qualname()

or:

    executing.Source.for_frame(frame).code_qualname(frame.f_code)

### The `Source` class

Everything goes through the `Source` class. Only one instance of the class is created for each filename. Subclassing it to add more attributes on creation or methods is recommended. The classmethods such as `executing` will respect this. See the source code and docstrings for more detail.

## Installation

    pip install executing

If you don't like that you can just copy the file `executing.py`, there are no dependencies (but of course you won't get updates).

## How does it work?

Suppose the frame is executing this line:

    self.foo(bar.x)

and in particular it's currently obtaining the attribute `self.foo`. Looking at the bytecode, specifically `frame.f_code.co_code[frame.f_lasti]`, we can tell that it's loading an attribute, but it's not obvious which one. We can narrow down the statement being executed using `frame.f_lineno` and find the two `ast.Attribute` nodes representing `self.foo` and `bar.x`. How do we find out which one it is, without recreating the entire compiler in Python?

The trick is to modify the AST slightly for each candidate expression and observe the changes in the bytecode instructions. We change the AST to this:

    (self.foo ** 'longuniqueconstant')(bar.x)
    
and compile it, and the bytecode will be almost the same but there will be two new instructions:

    LOAD_CONST 'longuniqueconstant'
    BINARY_POWER

and just before that will be a `LOAD_ATTR` instruction corresponding to `self.foo`. Seeing that it's in the same position as the original instruction lets us know we've found our match.

## Is it reliable?

Yes - if it identifies a node, you can trust that it's identified the correct one. The tests are very thorough - in addition to unit tests which check various situations directly, there are property tests against a large number of files (see the filenames printed in [this build](https://travis-ci.org/alexmojaki/executing/jobs/557970457)) with real code. Specifically, for each file, the tests:
 
 1. Identify as many nodes as possible from all the bytecode instructions in the file, and assert that they are all distinct
 2. Find all the nodes that should be identifiable, and assert that they were indeed identified somewhere

In other words, it shows that there is a one-to-one mapping between the nodes and the instructions that can be handled. This leaves very little room for a bug to creep in.

Furthermore, `executing` checks that the instructions compiled from the modified AST exactly match the original code save for a few small known exceptions. This accounts for all the quirks and optimisations in the interpreter. 

## Which nodes can it identify?

Currently it works in almost all cases for the following `ast` nodes:
 
 - `Call`, e.g. `self.foo(bar)`
 - `Attribute`, e.g. `point.x`
 - `Subscript`, e.g. `lst[1]`
 - `BinOp`, e.g. `x + y` (doesn't include `and` and `or`)
 - `UnaryOp`, e.g. `-n` (includes `not` but only works sometimes)
 - `Compare` e.g. `a < b` (not for chains such as `0 < p < 1`)

The plan is to extend to more operations in the future.