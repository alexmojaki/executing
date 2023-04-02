from .executing import EnhancedAST, NotOneValueFound, Source, only, function_node_types, assert_
from typing import Any, Callable, Iterator, Optional, Sequence, Set, Tuple, Type, Union, cast
import ast
import sys

py11 = sys.version_info >= (3, 11) # type: bool

def parents(node):
    # type: (EnhancedAST) -> Iterator[EnhancedAST] 
    while hasattr(node, "parent"):
        node = node.parent
        yield node


def has_parent(node, node_type):
    # type: (EnhancedAST,Union[Type,Tuple[Type,...]]) -> bool
    return any(isinstance(p, node_type) for p in parents(node))


def node_and_parents(node) :
    # type: (EnhancedAST) -> Iterator[EnhancedAST] 
    yield node
    for n in parents(node):
        yield n

def before(node):
    # type: (EnhancedAST) -> Iterator[EnhancedAST] 
    parent_list = only(
        l for _, l in ast.iter_fields(node.parent) if isinstance(l, list) and node in l
    )
    index = parent_list.index(node)
    return reversed(parent_list[:index])

