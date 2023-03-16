import ast
import sys
import dis
from types import CodeType, FrameType
from typing import Any, Callable, Iterator, Optional, Sequence, Set, Tuple, Type, Union, cast
from .executing import EnhancedAST, NotOneValueFound, Source, only, function_node_types, assert_
from ._exceptions import KnownIssue, VerifierFailure

from functools import lru_cache

# the code in this module can use all python>=3.11 features


def parents(node: EnhancedAST) -> Iterator[EnhancedAST]:
    while True:
        if hasattr(node, "parent"):
            node = node.parent
            yield node
        else:
            break  # pragma: no mutate


def node_and_parents(node: EnhancedAST) -> Iterator[EnhancedAST]:
    yield node
    yield from parents(node)


def mangled_name(node: EnhancedAST) -> str:
    """

    Parameters:
        node: the node which should be mangled
        name: the name of the node

    Returns:
        The mangled name of `node`
    """
    if isinstance(node, ast.Attribute):
        name = node.attr
    elif isinstance(node, ast.Name):
        name = node.id
    elif isinstance(node, (ast.alias)):
        name = node.asname or node.name.split(".")[0]
    elif isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
        name = node.name
    elif isinstance(node, ast.ExceptHandler):
        assert node.name
        name = node.name
    else:
        raise TypeError("no node to mangle")

    if name.startswith("__") and not name.endswith("__"):

        parent,child=node.parent,node

        while not (isinstance(parent,ast.ClassDef) and child not in parent.bases):
            if not hasattr(parent,"parent"):
                break # pragma: no mutate

            parent,child=parent.parent,parent
        else:
            class_name=parent.name.lstrip("_")
            if class_name!="":
                return "_" + class_name + name

            

    return name


@lru_cache(128) # pragma: no mutate
def get_instructions(code: CodeType) -> list[dis.Instruction]:
    return list(dis.get_instructions(code, show_caches=True))


types_cmp_issue_fix = (
    ast.IfExp,
    ast.If,
    ast.Assert,
    ast.While,
)

types_cmp_issue = types_cmp_issue_fix + (
    ast.ListComp,
    ast.SetComp,
    ast.DictComp,
    ast.GeneratorExp,
)

op_type_map = {
    "**": ast.Pow,
    "*": ast.Mult,
    "@": ast.MatMult,
    "//": ast.FloorDiv,
    "/": ast.Div,
    "%": ast.Mod,
    "+": ast.Add,
    "-": ast.Sub,
    "<<": ast.LShift,
    ">>": ast.RShift,
    "&": ast.BitAnd,
    "^": ast.BitXor,
    "|": ast.BitOr,
}


class BaseNodeFinder(object):


    @staticmethod
    def is_except_cleanup(inst: dis.Instruction, node: EnhancedAST) -> bool:
        if inst.opname not in (
            "STORE_NAME",
            "STORE_FAST",
            "STORE_DEREF",
            "STORE_GLOBAL",
            "DELETE_NAME",
            "DELETE_FAST",
            "DELETE_DEREF",
            "DELETE_GLOBAL",
        ):
            return False

        # This bytecode does something exception cleanup related.
        # The position of the instruciton seems to be something in the last ast-node of the ExceptHandler
        # this could be a bug, but it might not be observable in normal python code.

        # example:
        # except Exception as exc:
        #     enum_member._value_ = value

        # other example:
        # STORE_FAST of e was mapped to Constant(value=False)
        # except OSError as e:
        #     if not _ignore_error(e):
        #         raise
        #     return False

        # STORE_FAST of msg was mapped to print(...)
        #  except TypeError as msg:
        #      print("Sorry:", msg, file=file)

        if (
            isinstance(node, ast.Name)
            and isinstance(node.ctx,ast.Store)
            and inst.opname.startswith("STORE_")
            and mangled_name(node) == inst.argval
        ):
            # Storing the variable is valid and no exception cleanup, if the name is correct
            return False

        if (
            isinstance(node, ast.Name)
            and isinstance(node.ctx,ast.Del)
            and inst.opname.startswith("DELETE_")
            and mangled_name(node) == inst.argval
        ):
            # Deleting the variable is valid and no exception cleanup, if the name is correct
            return False

        return any(
            isinstance(n, ast.ExceptHandler) and n.name and mangled_name(n) == inst.argval
            for n in parents(node)
        )

    def verify(self, node: EnhancedAST, instruction: dis.Instruction) -> None:
        """
        checks if this node could gererate this instruction
        """

        op_name = instruction.opname
        extra_filter: Callable[[EnhancedAST], bool] = lambda e: True
        ctx: Type = type(None)

        def inst_match(opnames: Union[str, Sequence[str]], **kwargs: Any) -> bool:
            """
            match instruction

            Parameters:
                opnames: (str|Seq[str]): inst.opname has to be equal to or in `opname`
                **kwargs: every arg has to match inst.arg

            Returns:
                True if all conditions match the instruction

            """

            if isinstance(opnames, str):
                opnames = [opnames]
            return instruction.opname in opnames and kwargs == {
                k: getattr(instruction, k) for k in kwargs
            }

        def node_match(node_type: Union[Type, Tuple[Type, ...]], **kwargs: Any) -> bool:
            """
            match the ast-node

            Parameters:
                node_type: type of the node
                **kwargs: every `arg` has to be equal `node.arg`
                        or `node.arg` has to be an instance of `arg` if it is a type.
            """
            return isinstance(node, node_type) and all(
                isinstance(getattr(node, k), v)
                if isinstance(v, type)
                else getattr(node, k) == v
                for k, v in kwargs.items()
            )

        if op_name == "CACHE":
            return

        if inst_match("CALL") and node_match((ast.With, ast.AsyncWith)):
            # call to context.__exit__
            return

        if inst_match(("CALL", "LOAD_FAST")) and node_match(
            (ast.ListComp, ast.GeneratorExp, ast.SetComp, ast.DictComp)
        ):
            # call to the generator function
            return

        if inst_match(("CALL", "CALL_FUNCTION_EX")) and node_match(
            (ast.ClassDef, ast.Call)
        ):
            return

        if inst_match(("COMPARE_OP", "IS_OP", "CONTAINS_OP")) and node_match(
            ast.Compare
        ):
            return

        if inst_match("LOAD_NAME", argval="__annotations__") and node_match(
            ast.AnnAssign
        ):
            return

        if (
            (
                inst_match("LOAD_METHOD", argval="join")
                or inst_match(("CALL", "BUILD_STRING"))
            )
            and node_match(ast.BinOp, left=ast.Constant, op=ast.Mod)
            and isinstance(cast(ast.Constant, cast(ast.BinOp, node).left).value, str)
        ):
            # "..."%(...) uses "".join
            return

        if inst_match("STORE_SUBSCR") and node_match(ast.AnnAssign):
            # data: int
            return


        if inst_match(("DELETE_NAME", "DELETE_FAST")) and node_match(
            ast.Name, id=instruction.argval, ctx=ast.Del
        ):
            return

        if inst_match("BUILD_STRING") and (
            node_match(ast.JoinedStr) or node_match(ast.BinOp, op=ast.Mod)
        ):
            return

        if inst_match(("BEFORE_WITH","WITH_EXCEPT_START")) and node_match(ast.With):
            return

        if inst_match(("STORE_NAME", "STORE_GLOBAL"), argval="__doc__") and node_match(
            ast.Constant
        ):
            # store docstrings
            return

        if (
            inst_match(("STORE_NAME", "STORE_FAST", "STORE_GLOBAL", "STORE_DEREF"))
            and node_match(ast.ExceptHandler)
            and instruction.argval == mangled_name(node)
        ):
            # store exception in variable
            return

        if (
            inst_match(("STORE_NAME", "STORE_FAST", "STORE_DEREF", "STORE_GLOBAL"))
            and node_match((ast.Import, ast.ImportFrom))
            and any(mangled_name(cast(EnhancedAST, alias)) == instruction.argval for alias in cast(ast.Import, node).names)
        ):
            # store imported module in variable
            return

        if (
            inst_match(("STORE_FAST", "STORE_DEREF", "STORE_NAME", "STORE_GLOBAL"))
            and (
                node_match((ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef))
                or node_match(
                    ast.Name,
                    ctx=ast.Store,
                )
            )
            and instruction.argval == mangled_name(node)
        ):
            return

        if False:
            # TODO: match expressions are not supported for now
            if inst_match(("STORE_FAST", "STORE_NAME")) and node_match(
                ast.MatchAs, name=instruction.argval
            ):
                return

            if inst_match("COMPARE_OP", argval="==") and node_match(ast.MatchSequence):
                return

            if inst_match("COMPARE_OP", argval="==") and node_match(ast.MatchValue):
                return

        if inst_match("BINARY_OP") and node_match(
            ast.AugAssign, op=op_type_map[instruction.argrepr.removesuffix("=")]
        ):
            # a+=5
            return

        if node_match(ast.Attribute, ctx=ast.Del) and inst_match(
            "DELETE_ATTR", argval=mangled_name(node)
        ):
            return

        if inst_match(("JUMP_IF_TRUE_OR_POP", "JUMP_IF_FALSE_OR_POP")) and node_match(
            ast.BoolOp
        ):
            # and/or short circuit
            return

        if inst_match("DELETE_SUBSCR") and node_match(ast.Subscript, ctx=ast.Del):
            return

        if (
            node_match(ast.Name, ctx=ast.Load)
            or (
                node_match(ast.Name, ctx=ast.Store)
                and isinstance(node.parent, ast.AugAssign)
            )
        ) and inst_match(
            ("LOAD_NAME", "LOAD_FAST", "LOAD_GLOBAL", "LOAD_DEREF"), argval=mangled_name(node)
        ):
            return

        if node_match(ast.Name, ctx=ast.Del) and inst_match(
            ("DELETE_NAME", "DELETE_GLOBAL", "DELETE_DEREF"), argval=mangled_name(node)
        ):
            return

        # old verifier

        typ: Type = type(None)
        op_type: Type = type(None)

        if op_name.startswith(("BINARY_SUBSCR", "SLICE+")):
            typ = ast.Subscript
            ctx = ast.Load
        elif op_name.startswith("BINARY_"):
            typ = ast.BinOp
            op_type = op_type_map[instruction.argrepr]
            extra_filter = lambda e: isinstance(cast(ast.BinOp, e).op, op_type)
        elif op_name.startswith("UNARY_"):
            typ = ast.UnaryOp
            op_type = dict(
                UNARY_POSITIVE=ast.UAdd,
                UNARY_NEGATIVE=ast.USub,
                UNARY_NOT=ast.Not,
                UNARY_INVERT=ast.Invert,
            )[op_name]
            extra_filter = lambda e: isinstance(cast(ast.UnaryOp, e).op, op_type)
        elif op_name in ("LOAD_ATTR", "LOAD_METHOD", "LOOKUP_METHOD"):
            typ = ast.Attribute
            ctx = ast.Load
            extra_filter = lambda e: mangled_name(e) == instruction.argval
        elif op_name in (
            "LOAD_NAME",
            "LOAD_GLOBAL",
            "LOAD_FAST",
            "LOAD_DEREF",
            "LOAD_CLASSDEREF",
        ):
            typ = ast.Name
            ctx = ast.Load
            extra_filter = lambda e: cast(ast.Name, e).id == instruction.argval
        elif op_name in ("COMPARE_OP", "IS_OP", "CONTAINS_OP"):
            typ = ast.Compare
            extra_filter = lambda e: len(cast(ast.Compare, e).ops) == 1
        elif op_name.startswith(("STORE_SLICE", "STORE_SUBSCR")):
            ctx = ast.Store
            typ = ast.Subscript
        elif op_name.startswith("STORE_ATTR"):
            ctx = ast.Store
            typ = ast.Attribute
            extra_filter = lambda e: mangled_name(e) == instruction.argval

        node_ctx = getattr(node, "ctx", None)

        ctx_match = (
            ctx is not type(None)
            or not hasattr(node, "ctx")
            or isinstance(node_ctx, ctx)
        )

        # check for old verifier
        if isinstance(node, typ) and ctx_match and extra_filter(node):
            return

        # generate error

        title = "ast.%s is not created from %s" % (
            type(node).__name__,
            instruction.opname,
        )

        raise VerifierFailure(title, node, instruction)

