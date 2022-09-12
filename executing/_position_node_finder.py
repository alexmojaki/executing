import ast
import dis
from .executing import NotOneValueFound, only, function_node_types, attr_names_match, assert_
from ._exceptions import KnownIssue, VerifierFailure

from functools import lru_cache

# the code in this module can use all python>=3.11 features 


def node_and_parents(node):
    while True:
        yield node
        if hasattr(node, "parent"):
            node = node.parent
        else:
            break


class PositionNodeFinder(object):
    """
    Mapping bytecode to ast-node based on the source positions, which where introduced in pyhon 3.11.
    In general every ast-node can be exactly referenced by its begin/end line/col_offset, which is stored in the bytecode.
    There are only some exceptions for methods and attributes.
    """

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

    last_code = None
    last_instructions = None

    @staticmethod
    @lru_cache(8)
    def get_instructions(code):
        return list(dis.get_instructions(code, show_caches=True))

    def __init__(self, frame, stmts, tree, lasti, source):
        self.bc_list = self.get_instructions(frame.f_code)

        self.source = source

        try:
            # try to map with all match_positions
            node = self.find_node(lasti)
        except NotOneValueFound:
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
            elif self.opname(lasti) == "CALL":
                # A CALL instruction can be a method call, in which case the lineno and col_offset gets changed by the compiler.
                # Therefore we ignoring here this attributes and searchnig for a Call-node only by end_col_offset and end_lineno.
                # This is save, because there can only be one method ending at a specific point in the source code.
                # One closing ) only belongs to one method.
                typ = (ast.Call,)
            else:
                raise

            node = self.find_node(
                lasti,
                match_positions=("end_col_offset", "end_lineno"),
                typ=typ,
            )

        # report KnownIssues

        instruction = self.instruction(lasti)

        if instruction.opname in ("COMPARE_OP", "IS_OP", "CONTAINS_OP") and isinstance(
            node, self.types_cmp_issue
        ):
            if isinstance(node, self.types_cmp_issue_fix):
                # this is a workaround for https://github.com/python/cpython/issues/95921
                # we can fix cases with only on comparison inside the test condition
                #
                # we can not fix cases like:
                # if a<b<c and d<e<f: pass
                # if (a<b<c)!=d!=e: pass
                # because we don't know which comparison caused the problem

                comparisons = [
                    n
                    for n in ast.walk(node.test)
                    if isinstance(n, ast.Compare) and len(n.ops) > 1
                ]

                assert_(comparisons, "expected at least one comparison")

                if len(comparisons) == 1:
                    node = comparisons[0]
                else:
                    raise KnownIssue(
                        "multiple chain comparison inside %s can not be fixed" % (node)
                    )

            else:
                # Comprehension and generators get not fixed for now.
                raise KnownIssue("chain comparison inside %s can not be fixed" % (node))

        if isinstance(node, ast.Assert):
            # pytest assigns the position of the assertion to all expressions of the rewritten assertion.
            # All the rewritten expressions get mapped to ast.Assert, which is the wrong ast-node.
            # We don't report this wrong result.
            raise KnownIssue("assert")

        if any(isinstance(n, ast.pattern) for n in node_and_parents(node)):
            # TODO: investigate
            raise KnownIssue("pattern matching ranges seems to be wrong")

        if instruction.opname == "STORE_NAME" and instruction.argval == "__classcell__":
            # handle stores to __classcell__ as KnownIssue,
            # because they get complicated if they are used in `if` or `for` loops
            raise KnownIssue("define class member")

        # find decorators
        if (
            isinstance(node.parent, (ast.ClassDef, function_node_types))
            and node in node.parent.decorator_list
        ):
            node_func = node.parent
            index = lasti

            while True:
                # the generated bytecode looks like follow:

                # index    opname
                # ------------------
                # index-4  PRECALL
                # index-2  CACHE
                # index    CALL        <- the call instruction
                # ...      CACHE       some CACHE instructions

                # maybe multiple other bytecode blocks for other decorators
                # index-4  PRECALL
                # index-2  CACHE
                # index    CALL        <- index of the next loop
                # ...      CACHE       some CACHE instructions

                # index+x  STORE_*     the ast-node of this instruction points to the decorated thing

                if self.opname(index - 4) != "PRECALL" or self.opname(index) != "CALL":
                    break

                index += 2

                while self.opname(index) in ("CACHE", "EXTENDED_ARG"):
                    index += 2

                if self.find_node(index) == node_func and self.opname(index).startswith(
                    "STORE_"
                ):
                    self.result = node_func
                    self.decorator = node
                    return

                index += 4

        self.verify(node, self.instruction(lasti))

        self.result = node
        self.decorator = None

    def verify(self, node, instruction):
        """
        checks if this node could gererate this instruction
        """

        op_name = instruction.opname
        extra_filter = lambda e: True
        ctx = type(None)

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

        def except_cleanup(inst, node):

            if inst.opname not in (
                "STORE_NAME",
                "STORE_FAST",
                "STORE_DEREF",
                "DELETE_NAME",
                "DELETE_FAST",
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

            x = node
            while hasattr(x, "parent"):
                x = x.parent
                if isinstance(x, ast.ExceptHandler):
                    if (x.name or "exc") == inst.argval:
                        return True

            return False

        def inst_match(opname, **args):
            """
            match instruction

            Parameters:
                opname (string|Seq[stirng]): inst.opname has to be equal or in `opname`
                **args: every arg has to match inst.arg

            Returns:
                True if all conditions match the instruction

            """
            if isinstance(opname, tuple):
                if instruction.opname not in opname:
                    return False
            else:
                if instruction.opname != opname:
                    return False
            return all(getattr(instruction, k) == v for k, v in args.items())

        def node_match(node_type, **args):
            """
            match the ast-node

            Parameters:
                node_type: type of the node
                **args: every `arg` has to be equal `node.arg`
                        or `node.arg` has to be an instance of `arg` if it is a type.
            """
            return isinstance(node, node_type) and all(
                isinstance(getattr(node, k), v)
                if isinstance(v, type)
                else getattr(node, k) == v
                for k, v in args.items()
            )

        def mangled_name(node, name=None):
            """

            Parameters:
                node: the node which should be mangled
                name: the name of the node

            Returns:
                The mangled name of `node`
            """
            if name is None:
                if isinstance(node, ast.Attribute):
                    name = node.attr
                elif isinstance(node, ast.Name):
                    name = node.id
                else:
                    name = node.name

            if name.startswith("__") and not name.endswith("__"):
                parent = node.parent
                while True:
                    if isinstance(parent, ast.ClassDef):
                        return "_" + parent.name.lstrip("_") + name

                    if not hasattr(parent, "parent"):
                        break
                    parent = parent.parent

            return name

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

        if inst_match(("CALL", "CALL_FUNCTION_EX")) and node_match(ast.ClassDef):
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
            (inst_match("LOAD_METHOD", argval="join") or inst_match("CALL"))
            and node_match(ast.BinOp, left=ast.Constant, op=ast.Mod)
            and isinstance(node.left.value, str)
        ):
            # "..."%(...) uses "".join
            return

        if inst_match("STORE_SUBSCR") and node_match(ast.AnnAssign):
            # data: int
            return

        if except_cleanup(instruction, node):
            return

        if inst_match(("DELETE_NAME", "DELETE_FAST")) and node_match(
            ast.Name, id=instruction.argval, ctx=ast.Del
        ):
            return

        if inst_match("BUILD_STRING") and node_match(ast.BinOp, op=ast.Mod):
            return

        if inst_match("BUILD_STRING") and node_match(ast.JoinedStr):
            return

        if inst_match("BEFORE_WITH") and node_match(ast.With):
            return

        if inst_match(("STORE_NAME", "STORE_GLOBAL"), argval="__doc__") and node_match(
            ast.Constant
        ):
            # store docstrings
            return

        if inst_match(("STORE_NAME", "STORE_FAST", "STORE_DEREF")) and node_match(
            ast.ExceptHandler, name=instruction.argval
        ):
            # store exception in variable
            return

        if (
            inst_match(("STORE_NAME", "STORE_FAST", "STORE_DEREF", "STORE_GLOBAL"))
            and node_match((ast.Import, ast.ImportFrom))
            and any(
                mangled_name(alias, alias.asname or alias.name.split(".")[0])
                == instruction.argval
                for alias in node.names
            )
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
            # match expressions are not supported for now
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

        if inst_match(("CALL", "CALL_FUNCTION_EX")) and node_match(ast.Call):
            return

        if node_match(ast.Name, ctx=ast.Load) and inst_match(
            ("LOAD_NAME", "LOAD_GLOBAL"), argval=mangled_name(node)
        ):
            return

        if node_match(ast.Name, ctx=ast.Del) and inst_match(
            ("DELETE_NAME", "DELETE_GLOBAL"), argval=mangled_name(node)
        ):
            return

        # old verifier

        typ = type(None)

        if op_name.startswith(("BINARY_SUBSCR", "SLICE+")):
            typ = ast.Subscript
            ctx = ast.Load
        elif op_name.startswith("BINARY_"):
            typ = ast.BinOp
            op_type = op_type_map[instruction.argrepr]
            extra_filter = lambda e: isinstance(e.op, op_type)
        elif op_name.startswith("UNARY_"):
            typ = ast.UnaryOp
            op_type = dict(
                UNARY_POSITIVE=ast.UAdd,
                UNARY_NEGATIVE=ast.USub,
                UNARY_NOT=ast.Not,
                UNARY_INVERT=ast.Invert,
            )[op_name]
            extra_filter = lambda e: isinstance(e.op, op_type)
        elif op_name in ("LOAD_ATTR", "LOAD_METHOD", "LOOKUP_METHOD"):
            typ = ast.Attribute
            ctx = ast.Load
            extra_filter = lambda e: attr_names_match(e.attr, instruction.argval)
        elif op_name in (
            "LOAD_NAME",
            "LOAD_GLOBAL",
            "LOAD_FAST",
            "LOAD_DEREF",
            "LOAD_CLASSDEREF",
        ):
            typ = ast.Name
            ctx = ast.Load
            extra_filter = lambda e: e.id == instruction.argval
        elif op_name in ("COMPARE_OP", "IS_OP", "CONTAINS_OP"):
            typ = ast.Compare
            extra_filter = lambda e: len(e.ops) == 1
        elif op_name.startswith(("STORE_SLICE", "STORE_SUBSCR")):
            ctx = ast.Store
            typ = ast.Subscript
        elif op_name.startswith("STORE_ATTR"):
            ctx = ast.Store
            typ = ast.Attribute
            extra_filter = lambda e: attr_names_match(e.attr, instruction.argval)

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

    def instruction(self, index):
        return self.bc_list[index // 2]

    def opname(self, index):
        return self.instruction(index).opname

    def find_node(
        self,
        index,
        match_positions=("lineno", "end_lineno", "col_offset", "end_col_offset"),
        typ=(ast.expr, ast.stmt, ast.excepthandler, ast.pattern),
    ):
        position = self.instruction(index).positions

        return only(
            node
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
