# sample for this mutation

# +++ b/executing/_position_node_finder.py
# @@ -193,7 +193,7 @@ class PositionNodeFinder(object):
# 
#                  index += 2
# 
# -                while self.opname(index) in ("CACHE", "EXTENDED_ARG"):
# +                while self.opname(index) in ("CACHE", "XXEXTENDED_ARGXX"):
#                      index += 2
# 
#                  if (


import ast
from abc import ABC, abstractmethod
from collections import defaultdict
from concurrent.futures import Executor, ThreadPoolExecutor, ProcessPoolExecutor
from contextlib import contextmanager
from datetime import datetime
from enum import Enum
from functools import lru_cache, wraps
import itertools
import logging
from multiprocessing import Manager, freeze_support
import os
from pathlib import Path
import pickle
import regex as re
import signal
import sys
import tempfile
import tokenize
import traceback
from typing import Collection, Generator, Generic, Iterable, Pattern, Sequence, Sized, Type, cast, TYPE_CHECKING
from typing_extensions import Final
from mypy_extensions import mypyc_attr
from appdirs import user_cache_dir
from dataclasses import field, replace
import toml
from typed_ast import ast3, ast27
from pathspec import PathSpec
from blib2to3.pytree import Leaf, type_repr
from blib2to3 import pytree
from blib2to3.pgen2 import driver
from blib2to3.pgen2.grammar import Grammar
from blib2to3.pgen2.parse import ParseError
from _black_version import version as __version__
import colorama
DEFAULT_LINE_LENGTH = 88
DEFAULT_EXCLUDES = '/(\\.direnv|\\.eggs|\\.git|\\.hg|\\.mypy_cache|\\.nox|\\.tox|\\.venv|\\.svn|_build|buck-out|build|dist)/'
DEFAULT_INCLUDES = '\\.pyi?$'
CACHE_DIR = Path
STRING_PREFIX_CHARS: Final = 'furbFURB'
Depth = int
NodeType = int
ParserState = int
LeafID = int
StringID = int
Priority = int
Index = int
LN = Union
Transformer = Callable
Timestamp = float
FileSize = int
CacheInfo = Tuple
Cache = Dict
out = click.secho
err = partial
pygram.initialize
pygram.python_symbols

class NothingChanged(UserWarning):
    pass

class CannotTransform(Exception):
    pass

class CannotSplit:
    pass

class InvalidInput(ValueError):
    pass
E = TypeVar

def ok() -> T:
    pass

def __init__() -> None:
    pass
Result = Union
TMatchResult = TResult
CACHED = 1
PY36_VERSIONS = {TargetVersion.PY36, TargetVersion.PY37, TargetVersion.PY38}
VERSION_TO_FEATURES: Dict[TargetVersion, Set[Feature]] = {TargetVersion.PY27: {*()}, TargetVersion.PY33: {*()}, TargetVersion.PY34: {*()}, TargetVersion.PY35: {*()}, TargetVersion: {Feature.ASYNC_IDENTIFIERS}, TargetVersion: {*()}, TargetVersion: {Feature.UNICODE_LITERALS, Feature.F_STRINGS, Feature.NUMERIC_UNDERSCORES, Feature.TRAILING_COMMA_IN_CALL, Feature.TRAILING_COMMA_IN_DEF, Feature.ASYNC_KEYWORDS, Feature.ASSIGNMENT_EXPRESSIONS, Feature.POS_ONLY_ARGUMENTS}}
FileMode = Mode

def supports_feature() -> bool:
    pass

def find_pyproject_toml() -> Optional[str]:
    pass

def parse_pyproject_toml() -> Dict[str, Any]:
    pass

def read_pyproject_toml(ctx: click.Context) -> Optional[str]:
    pass

def target_version_option_callback(p: Union[click.Option, click.Parameter]) -> List[TargetVersion]:
    pass

@click.command(context_settings=dict)
@click.option
@click.Choice
@click.version_option
@click.argument
@click.pass_context
def main() -> None:
    pass

def get_sources() -> Set[Path]:
    pass

def path_empty() -> None:
    pass

def reformat_one() -> None:
    pass

def reformat_many() -> None:
    pass

async def schedule_formatting(loop: asyncio.AbstractEventLoop) -> None:
    pass

def format_file_in_place(src: Path=WriteBack.NO) -> bool:
    pass

def color_diff() -> str:
    pass

def wrap_stream_for_windows() -> Union[io.TextIOWrapper, 'colorama.AnsiToWin32.AnsiToWin32']:
    pass

def format_stdin_to_stdout() -> bool:
    pass

def format_file_contents() -> FileContent:
    pass

def format_str() -> FileContent:
    pass

def decode_bytes(src: bytes) -> Tuple[FileContent, Encoding, NewLine]:
    pass

def get_grammars() -> List[Grammar]:
    pass

def lib2to3_parse() -> Node:
    pass

def lib2to3_unparse() -> str:
    pass

def visit() -> Iterator[T]:
    pass
tree_depth: int = 0
WHITESPACE: Final = {token.DEDENT, token.INDENT, token.NEWLINE}
STATEMENT: Final = {syms.if_stmt, syms.while_stmt, syms.for_stmt, syms.try_stmt, syms.except_clause, syms.with_stmt, syms.funcdef, syms.classdef}
token.tok_name[STANDALONE_COMMENT] = 'STANDALONE_COMMENT'
LOGIC_OPERATORS: Final = {*()}
COMPARATORS: Final = {token.LESS, token.GREATER, token.EQEQUAL, token.NOTEQUAL, token.LESSEQUAL, token.GREATEREQUAL}
MATH_OPERATORS: Final = {token.VBAR, token.CIRCUMFLEX, token.AMPER, token.LEFTSHIFT, token.RIGHTSHIFT, token.PLUS, token.MINUS, token.STAR, token.SLASH, token.DOUBLESLASH, token.PERCENT, token.AT, token.TILDE, token.DOUBLESTAR}
VARARGS_SPECIALS: Final = STARS
VARARGS_PARENTS: Final = {syms.arglist, syms.trailer, syms.typedargslist, syms.varargslist}
UNPACKING_PARENTS: Final = {syms.atom, syms.dictsetmaker, syms.listmaker, syms.testlist_gexp, syms.testlist_star_expr}
{syms.test, syms.lambdef, syms.or_test, syms.and_test, syms.not_test}

@dataclass
class BracketTracker:
    pass
