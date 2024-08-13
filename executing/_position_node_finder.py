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
    elif sys.version_info >= (3,12) and isinstance(node,ast.TypeVar):
        name=node.name
    else:
        raise TypeError("no node to mangle for type "+repr(type(node)))

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
    return list(dis.get_instructions(code))


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


class PositionNodeFinder(object):
    """
    Mapping bytecode to ast-node based on the source positions, which where introduced in pyhon 3.11.
    In general every ast-node can be exactly referenced by its begin/end line/col_offset, which is stored in the bytecode.
    There are only some exceptions for methods and attributes.
    """

    def __init__(self, frame: FrameType, stmts: Set[EnhancedAST], tree: ast.Module, lasti: int, source: Source):
        self.bc_dict={bc.offset:bc for bc in get_instructions(frame.f_code) }

        self.source = source
        self.decorator: Optional[EnhancedAST] = None

        # work around for https://github.com/python/cpython/issues/96970
        while self.opname(lasti) == "CACHE":
            lasti -= 2

        try:
            # try to map with all match_positions
            self.result = self.find_node(lasti)
        except NotOneValueFound:
            typ: tuple[Type]
            # LOAD_METHOD could load "".join for long "..."%(...) BinOps
            # this can only be associated by using all positions
            if self.opname(lasti) in (
                "LOAD_METHOD",
                "LOAD_ATTR",
                "STORE_ATTR",
                "DELETE_ATTR",
            ):
                # lineno and col_offset of LOAD_METHOD and *_ATTR instructions get set to the beginning of
                # the attribute by the python compiler to improved error messages (PEP-657)
                # we ignore here the start position and try to find the ast-node just by end position and expected node type
                # This is save, because there can only be one attribute ending at a specific point in the source code.
                typ = (ast.Attribute,)
            elif self.opname(lasti) in ("CALL", "CALL_KW"):
                # A CALL instruction can be a method call, in which case the lineno and col_offset gets changed by the compiler.
                # Therefore we ignoring here this attributes and searchnig for a Call-node only by end_col_offset and end_lineno.
                # This is save, because there can only be one method ending at a specific point in the source code.
                # One closing ) only belongs to one method.
                typ = (ast.Call,)
            else:
                raise

            self.result = self.find_node(
                lasti,
                match_positions=("end_col_offset", "end_lineno"),
                typ=typ,
            )

        instruction = self.instruction(lasti)
        assert instruction is not None

        self.result = self.fix_result(self.result, instruction)

        self.known_issues(self.result, instruction)

        self.test_for_decorator(self.result, lasti)

        # verify
        if self.decorator is None:
            self.verify(self.result, instruction)
        else: 
            assert_(self.decorator in self.result.decorator_list)

    def test_for_decorator(self, node: EnhancedAST, index: int) -> None:
        if (
            isinstance(node.parent, (ast.ClassDef, function_node_types))
            and node in node.parent.decorator_list # type: ignore[attr-defined]
        ):
            node_func = node.parent

            while True:
                # the generated bytecode looks like follow:

                # index    opname
                # ------------------
                # index-4  PRECALL     (only in 3.11)
                # index-2  CACHE
                # index    CALL        <- the call instruction
                # ...      CACHE       some CACHE instructions

                # maybe multiple other bytecode blocks for other decorators
                # index-4  PRECALL     (only in 3.11)
                # index-2  CACHE
                # index    CALL        <- index of the next loop
                # ...      CACHE       some CACHE instructions

                # index+x  STORE_*     the ast-node of this instruction points to the decorated thing

                if not (
                    (self.opname(index - 4) == "PRECALL" or sys.version_info >= (3, 12))
                    and self.opname(index) == "CALL"
                ):  # pragma: no mutate
                    break  # pragma: no mutate

                index += 2

                while self.opname(index) in ("CACHE", "EXTENDED_ARG"):
                    index += 2

                if (
                    self.opname(index).startswith("STORE_")
                    and self.find_node(index) == node_func
                ):
                    self.result = node_func
                    self.decorator = node
                    return

                if sys.version_info < (3, 12):
                    index += 4

    def fix_result(
        self, node: EnhancedAST, instruction: dis.Instruction
    ) -> EnhancedAST:
        if (
            sys.version_info >= (3, 12, 5)
            and instruction.opname in ("GET_ITER", "FOR_ITER")
            and isinstance(node.parent, ast.For)
            and node is node.parent.iter
        ):
            # node positions have changed in 3.12.5
            # https://github.com/python/cpython/issues/93691
            # `for` calls __iter__ and __next__ during execution, the calling
            # expression of these calls was the ast.For node since cpython 3.11 (see test_iter).
            # cpython 3.12.5 changed this to the `iter` node of the loop, to make tracebacks easier to read.
            # This keeps backward compatibility with older executing versions.

            # there are also cases like:
            #
            # for a in iter(l): pass
            #
            # where `iter(l)` would be otherwise the resulting node for the `iter()` call and the __iter__ call of the for implementation.
            # keeping the old behaviour makes it possible to distinguish both cases.

            return node.parent
        return node

    def known_issues(self, node: EnhancedAST, instruction: dis.Instruction) -> None:
        if instruction.opname in ("COMPARE_OP", "IS_OP", "CONTAINS_OP") and isinstance(
            node, types_cmp_issue
        ):
            if isinstance(node, types_cmp_issue_fix):
                # this is a workaround for https://github.com/python/cpython/issues/95921
                # we can fix cases with only on comparison inside the test condition
                #
                # we can not fix cases like:
                # if a<b<c and d<e<f: pass
                # if (a<b<c)!=d!=e: pass
                # because we don't know which comparison caused the problem

                comparisons = [
                    n
                    for n in ast.walk(node.test) # type: ignore[attr-defined]
                    if isinstance(n, ast.Compare) and len(n.ops) > 1
                ]

                assert_(comparisons, "expected at least one comparison")

                if len(comparisons) == 1:
                    node = self.result = cast(EnhancedAST, comparisons[0])
                else:
                    raise KnownIssue(
                        "multiple chain comparison inside %s can not be fixed" % (node)
                    )

            else:
                # Comprehension and generators get not fixed for now.
                raise KnownIssue("chain comparison inside %s can not be fixed" % (node))

        if (
            sys.version_info[:3] == (3, 11, 1)
            and isinstance(node, ast.Compare)
            and instruction.opname == "CALL"
            and any(isinstance(n, ast.Assert) for n in node_and_parents(node))
        ):
            raise KnownIssue(
                "known bug in 3.11.1 https://github.com/python/cpython/issues/95921"
            )

        if isinstance(node, ast.Assert):
            # pytest assigns the position of the assertion to all expressions of the rewritten assertion.
            # All the rewritten expressions get mapped to ast.Assert, which is the wrong ast-node.
            # We don't report this wrong result.
            raise KnownIssue("assert")

        if any(isinstance(n, ast.pattern) for n in node_and_parents(node)):
            # TODO: investigate
            raise KnownIssue("pattern matching ranges seems to be wrong")

        if (
            sys.version_info >= (3, 12)
            and isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "super"
        ):
            # super is optimized to some instructions which do not map nicely to a Call

            # find the enclosing function
            func = node.parent
            while hasattr(func, "parent") and not isinstance(
                func, (ast.AsyncFunctionDef, ast.FunctionDef)
            ):

                func = func.parent

            # get the first function argument (self/cls)
            first_arg = None

            if hasattr(func, "args"):
                args = [*func.args.posonlyargs, *func.args.args]
                if args:
                    first_arg = args[0].arg

            if (instruction.opname, instruction.argval) in [
                ("LOAD_DEREF", "__class__"),
                ("LOAD_FAST", first_arg),
                ("LOAD_DEREF", first_arg),
            ]:
                raise KnownIssue("super optimization")

        if self.is_except_cleanup(instruction, node):
            raise KnownIssue("exeption cleanup does not belong to the last node in a except block")

        if instruction.opname == "STORE_NAME" and instruction.argval == "__classcell__":
            # handle stores to __classcell__ as KnownIssue,
            # because they get complicated if they are used in `if` or `for` loops
            # example:
            #
            # class X:
            #     # ... something
            #     if some_condition:
            #         def method(self):
            #             super()
            #
            # The `STORE_NAME` instruction gets mapped to the `ast.If` node,
            # because it is the last element in the class.
            # This last element could be anything and gets dificult to verify.

            raise KnownIssue("store __classcell__")

        if (
            instruction.opname == "CALL"
            and not isinstance(node,ast.Call)
            and any(isinstance(p, ast.Assert) for p in parents(node))
            and sys.version_info >= (3, 11, 2)
        ):
            raise KnownIssue("exception generation maps to condition")

        if sys.version_info >= (3, 13):
            if instruction.opname in (
                "STORE_FAST_STORE_FAST",
                "STORE_FAST_LOAD_FAST",
                "LOAD_FAST_LOAD_FAST",
            ):
                raise KnownIssue(f"can not map {instruction.opname} to two ast nodes")

            if instruction.opname == "LOAD_FAST" and instruction.argval == "__class__":
                raise KnownIssue(
                    f"loading of __class__ is accociated with a random node at the end of a class"
                )

            if (
                instruction.opname == "COMPARE_OP"
                and isinstance(node, ast.UnaryOp)
                and isinstance(node.operand,ast.Compare)
                and isinstance(node.op, ast.Not)
            ):
                # work around for 
                # https://github.com/python/cpython/issues/114671
                self.result = node.operand

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

        if (
            sys.version_info >= (3, 12)
            and inst_match(("LOAD_FAST_AND_CLEAR", "STORE_FAST"))
            and node_match((ast.ListComp, ast.SetComp, ast.DictComp))
        ):
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
                or inst_match("LOAD_ATTR", argval="join")  # 3.12
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

        if inst_match(
            (
                "JUMP_IF_TRUE_OR_POP",
                "JUMP_IF_FALSE_OR_POP",
                "POP_JUMP_IF_TRUE",
                "POP_JUMP_IF_FALSE",
            )
        ) and node_match(ast.BoolOp):
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
            (
                "LOAD_NAME",
                "LOAD_FAST",
                "LOAD_FAST_CHECK",
                "LOAD_GLOBAL",
                "LOAD_DEREF",
                "LOAD_FROM_DICT_OR_DEREF",
            ),
            argval=mangled_name(node),
        ):
            return

        if node_match(ast.Name, ctx=ast.Del) and inst_match(
            ("DELETE_NAME", "DELETE_GLOBAL", "DELETE_DEREF"), argval=mangled_name(node)
        ):
            return

        if node_match(ast.Constant) and inst_match(
            "LOAD_CONST", argval=cast(ast.Constant, node).value
        ):
            return

        if node_match(
            (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp, ast.For)
        ) and inst_match(("GET_ITER", "FOR_ITER")):
            return

        if sys.version_info >= (3, 12):
            if node_match(ast.UnaryOp, op=ast.UAdd) and inst_match(
                "CALL_INTRINSIC_1", argrepr="INTRINSIC_UNARY_POSITIVE"
            ):
                return

            if node_match(ast.Subscript) and inst_match("BINARY_SLICE"):
                return

            if node_match(ast.ImportFrom) and inst_match(
                "CALL_INTRINSIC_1", argrepr="INTRINSIC_IMPORT_STAR"
            ):
                return

            if (
                node_match(ast.Yield) or isinstance(node.parent, ast.GeneratorExp)
            ) and inst_match("CALL_INTRINSIC_1", argrepr="INTRINSIC_ASYNC_GEN_WRAP"):
                return

            if node_match(ast.Name) and inst_match("LOAD_DEREF",argval="__classdict__"):
                return

            if node_match(ast.TypeVar) and (
                inst_match("CALL_INTRINSIC_1", argrepr="INTRINSIC_TYPEVAR")
                or inst_match(
                    "CALL_INTRINSIC_2", argrepr="INTRINSIC_TYPEVAR_WITH_BOUND"
                )
                or inst_match(
                    "CALL_INTRINSIC_2", argrepr="INTRINSIC_TYPEVAR_WITH_CONSTRAINTS"
                )
                or inst_match(("STORE_FAST", "STORE_DEREF"), argrepr=mangled_name(node))
            ):
                return

            if node_match(ast.TypeVarTuple) and (
                inst_match("CALL_INTRINSIC_1", argrepr="INTRINSIC_TYPEVARTUPLE")
                or inst_match(("STORE_FAST", "STORE_DEREF"), argrepr=node.name)
            ):
                return

            if node_match(ast.ParamSpec) and (
                inst_match("CALL_INTRINSIC_1", argrepr="INTRINSIC_PARAMSPEC")

                or inst_match(("STORE_FAST", "STORE_DEREF"), argrepr=node.name)):
                return


            if node_match(ast.TypeAlias):
                if(
                    inst_match("CALL_INTRINSIC_1", argrepr="INTRINSIC_TYPEALIAS")
                    or inst_match(
                        ("STORE_NAME", "STORE_FAST", "STORE_DEREF"), argrepr=node.name.id
                    )
                    or inst_match("CALL")
                ):
                    return


            if node_match(ast.ClassDef) and node.type_params:
                if inst_match(
                    ("STORE_DEREF", "LOAD_DEREF", "LOAD_FROM_DICT_OR_DEREF"),
                    argrepr=".type_params",
                ):
                    return

                if inst_match(("STORE_FAST", "LOAD_FAST"), argrepr=".generic_base"):
                    return

                if inst_match(
                    "CALL_INTRINSIC_1", argrepr="INTRINSIC_SUBSCRIPT_GENERIC"
                ):
                    return

                if inst_match("LOAD_DEREF",argval="__classdict__"):
                    return

            if node_match((ast.FunctionDef,ast.AsyncFunctionDef)) and node.type_params:
                if inst_match("CALL"):
                    return

                if inst_match(
                    "CALL_INTRINSIC_2", argrepr="INTRINSIC_SET_FUNCTION_TYPE_PARAMS"
                ):
                    return

                if inst_match("LOAD_FAST",argval=".defaults"):
                    return

                if inst_match("LOAD_FAST",argval=".kwdefaults"):
                    return

            if inst_match("STORE_NAME", argval="__classdictcell__"):
                # this is a general thing
                return


            # f-strings

            if node_match(ast.JoinedStr) and (
                inst_match("LOAD_ATTR", argval="join")
                or inst_match(("LIST_APPEND", "CALL"))
            ):
                return

            if node_match(ast.FormattedValue) and inst_match("FORMAT_VALUE"):
                return

        if sys.version_info >= (3, 13):
            if (
                node_match(ast.FunctionDef)
                and inst_match("LOAD_CONST")
                and node.name == instruction.argval.co_name
            ):
                return

            if inst_match("NOP"):
                return

            if inst_match("TO_BOOL") and node_match(ast.BoolOp):
                return

            if inst_match("CALL_KW") and node_match((ast.Call, ast.ClassDef)):
                return

            if inst_match("LOAD_FAST", argval=".type_params"):
                return

            if inst_match("LOAD_FAST", argval="__classdict__"):
                return

            if inst_match("LOAD_FAST") and node_match(
                (
                    ast.FunctionDef,
                    ast.ClassDef,
                    ast.TypeAlias,
                    ast.TypeVar,
                    ast.Lambda,
                    ast.AsyncFunctionDef,
                )
            ):
                # closures
                # TODO: better check that this is actualy a closure variable
                return

            if (
                inst_match("LOAD_FAST")
                and node_match(ast.TypeAlias)
                and node.name.id == instruction.argval
            ):
                return

            if inst_match("STORE_NAME",argval="__static_attributes__"):
                # the node is the first node in the body
                return

            if inst_match("LOAD_FAST") and isinstance(node.parent,ast.TypeVar):
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
        elif op_name in ("LOAD_ATTR", "LOAD_METHOD", "LOOKUP_METHOD","LOAD_SUPER_ATTR"):
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

    def instruction(self, index: int) -> Optional[dis.Instruction]:
        return self.bc_dict.get(index,None)

    def opname(self, index: int) -> str:
        i=self.instruction(index)
        if i is None:
            return "CACHE"
        return i.opname

    extra_node_types=()
    if sys.version_info >= (3,12):
        extra_node_types = (ast.type_param,)

    def find_node(
        self,
        index: int,
        match_positions: Sequence[str] = (
            "lineno",
            "end_lineno",
            "col_offset",
            "end_col_offset",
        ),
        typ: tuple[Type, ...] = (
            ast.expr,
            ast.stmt,
            ast.excepthandler,
            ast.pattern,
            *extra_node_types,
        ),
    ) -> EnhancedAST:
        instruction = self.instruction(index)
        assert instruction is not None

        position = instruction.positions
        assert position is not None and position.lineno is not None

        return only(
            cast(EnhancedAST, node)
            for node in self.source._nodes_by_line[position.lineno]
            if isinstance(node, typ)
            if not isinstance(node, ast.Expr)
            # matchvalue.value has the same positions as matchvalue themself, so we exclude ast.MatchValue
            if not isinstance(node, ast.MatchValue)
            if all(
                getattr(position, attr) == getattr(node, attr)
                for attr in match_positions
            )
        )
