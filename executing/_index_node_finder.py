from __future__ import annotations  # type: ignore[attr-defined]

import sys

assert (
    (3, 8) <= sys.version_info < (3, 11)
), "This NodeFinder can only be used for python 3.8, 3.9 and 3.10"


import copy
import ast
import dis
import math
from types import FrameType
from typing import (
    Sequence,
    Iterable,
    Set,
    Callable,
    Tuple,
    List,
    Optional,
    Iterator,
    Dict,
    TypeVar,
    Union,
    Any,
    cast,
)
from dataclasses import dataclass


from .executing import (
    EnhancedAST,
    NotOneValueFound,
    Source,
    function_node_types,
    assert_,
    TESTING,
)

from ._exceptions import KnownIssue, MultipleMatches, NoMatch

from functools import lru_cache
from collections import defaultdict, namedtuple
from types import CodeType

from ._base_node_finder import BaseNodeFinder
from ._helper import node_and_parents, has_parent


# the main reason for this rewrite hooks is pytest,
# because we want to support the rewritten asserts in tests
pytest_rewrite_assert: Any

try:
    from _pytest.assertion.rewrite import rewrite_asserts as pytest_rewrite_assert
except:  # pragma: no cover
    pytest_rewrite_assert = None


Match = namedtuple("Match", "nodes code index_code")


def all_equal(seq: Iterator[Any]) -> bool:
    s, *rest = seq
    return all(s == e for e in rest)


@dataclass
class InstFingerprint:
    opcode: int
    value: Any
    line: Optional[int]
    offset: int
    index: int
    next: Tuple[int, ...]

    @property
    def opname(self) -> str:
        # only used for debugging
        return dis.opname[self.opcode]  # pragma: no cover

def normalize_opcode(opcode:int) -> int:
    if opcode==opcodes.PRINT_EXPR:
        # PRINT_EXPR is used for expression evaluation in the (i)python-repl 
        return opcodes.POP_TOP
    return opcode

def normalize(value: Any) -> Any:
    """normalize nan

    normalize nan to a random float because nan!=nan
    This would otherwise be a problem for the key lookup in CodeMap
    """
    if isinstance(value, float) and math.isnan(value):
        return 0.424420436760876254610289124609191284195
    elif isinstance(value, tuple):
        return tuple(normalize(v) for v in value)
    elif isinstance(value, complex):
        return complex(normalize(value.real), normalize(value.imag))
    elif isinstance(value, CodeType):
        return tuple(
            (normalize_opcode(inst.opcode), inst.offset, normalize(inst.argval))
            for inst in dis.get_instructions(value)
        )
    return value


class OpCodes:
    def __getattr__(self, name: str) -> int:
        # getattr makes mypy happy
        assert False, "%s is not a valid opcode" % name


for key, value in dis.opmap.items():
    setattr(OpCodes, key, value)

opcodes = OpCodes()

hasjcond = [
    opcodes.POP_JUMP_IF_TRUE,
    opcodes.POP_JUMP_IF_FALSE,
    opcodes.JUMP_IF_TRUE_OR_POP,
    opcodes.JUMP_IF_FALSE_OR_POP,
]

end_of_block = [opcodes.RETURN_VALUE, opcodes.RAISE_VARARGS]

skip_opcodes = (opcodes.NOP, opcodes.EXTENDED_ARG)


if sys.version_info >= (3, 9):
    hasjcond += [opcodes.JUMP_IF_NOT_EXC_MATCH]
    end_of_block += [opcodes.RERAISE]


class CodeFingerprint:
    def __init__(
        self, code: CodeType, lineno_map: Callable[[int], Optional[int]] = lambda a: a
    ):
        self.graph: Dict[int, InstFingerprint] = {}

        self.instructions: List[dis.Instruction] = []

        last_lineno = None
        for inst in dis.get_instructions(code):
            if inst.starts_line:
                last_lineno = inst.starts_line
            self.instructions.append(inst._replace(starts_line=last_lineno))

        assert all(i.offset == j * 2 for j, i in enumerate(self.instructions))

        def get_next(n: int) -> List[Tuple[int, Any]]:
            i = current_offset // 2
            return [(inst.opcode, inst.argval) for inst in self.instructions[i : i + n]]

        self.start = self.skip(0)

        todo = [self.start] if self.start is not None else []

        while todo:
            current_offset = todo.pop()
            next_offset = current_offset + 2
            inst = self.instructions[current_offset // 2]

            opcode = inst.opcode
            value = inst.argval

            optimize_result = self.optimize_tuple(inst)

            if optimize_result is not None:
                opcode, value, next_offset = optimize_result

            if get_next(2) == [(opcodes.BUILD_TUPLE, 2), (opcodes.UNPACK_SEQUENCE, 2)]:
                # normalize tuple optimization
                opcode = opcodes.ROT_TWO
                value = None
                next_offset += 2

            next_offsets: List[int] = []

            def add_offset(offset: Union[int, None]) -> None:
                if offset is not None:
                    next_offsets.append(offset)

            add_offset(self.skip(next_offset))

            if opcode in hasjcond:
                # this is also optimized by the python compiler if both instructions are on the same line
                # see https://github.com/python/cpython/issues/100378#issuecomment-1360381947
                next_offset = inst.argval
                if inst.opcode in [
                    opcodes.JUMP_IF_TRUE_OR_POP,
                    opcodes.JUMP_IF_FALSE_OR_POP,
                ]:
                    opcode, next_offset = self.optimize_jump(inst)

                add_offset(self.skip(next_offset))

            if inst.opcode in (
                opcodes.SETUP_FINALLY,
                opcodes.SETUP_WITH,
                opcodes.SETUP_ASYNC_WITH,
                opcodes.FOR_ITER,
            ):
                add_offset(self.skip(inst.argval))

            if inst.opcode in end_of_block:
                next_offsets = []

            for offset in next_offsets:
                if offset not in self.graph:
                    todo.append(offset)

            self.graph[current_offset] = InstFingerprint(
                opcode,
                value,
                line=lineno_map(cast(int, inst.starts_line)),
                offset=inst.offset,
                index=cast(int, inst.starts_line),
                next=tuple(next_offsets),
            )

    def next_opcode(self, offset: int) -> Optional[dis.Instruction]:
        done = set()
        while offset // 2 < len(self.instructions) and offset not in done:
            done.add(offset)
            inst = self.instructions[offset // 2]
            if inst.opcode in skip_opcodes:
                offset += 2
            elif inst.opcode in (opcodes.JUMP_FORWARD, opcodes.JUMP_ABSOLUTE):
                offset = inst.argval
            else:
                return inst
        return None

    def skip(self, offset: int) -> Optional[int]:
        inst = self.next_opcode(offset)
        if inst is not None:
            return inst.offset
        return None

    def follow_jump(self, offset: int) -> dis.Instruction:
        inst = self.next_opcode(offset)

        # follow jump is used in optimize_jump, which is only used for instructions like JUMP_IF_X_OR_POP
        # JUMP_IF_X_OR_POP is only generated for code like:
        # a = b or c
        # there can never be a loop and therefor next_opcode can never return None
        assert inst is not None

        return inst

    def optimize_jump(self, inst: dis.Instruction) -> Tuple[int, int]:
        pop = False
        if inst.opcode == opcodes.JUMP_IF_FALSE_OR_POP:
            # TOS=False
            jump_or_pop = opcodes.JUMP_IF_FALSE_OR_POP
            pop_and_no_jump = (opcodes.JUMP_IF_TRUE_OR_POP, opcodes.POP_JUMP_IF_TRUE)

            pop_and_jump = opcodes.POP_JUMP_IF_FALSE

        elif inst.opcode == opcodes.JUMP_IF_TRUE_OR_POP:
            # TOS=True
            jump_or_pop = opcodes.JUMP_IF_TRUE_OR_POP
            pop_and_no_jump = (opcodes.JUMP_IF_FALSE_OR_POP, opcodes.POP_JUMP_IF_FALSE)

            pop_and_jump = opcodes.POP_JUMP_IF_TRUE

        else:
            assert False, inst

        while inst.opcode == jump_or_pop:
            inst = self.follow_jump(inst.argval)

        if inst.opcode == pop_and_jump:
            pop = True
            inst = self.follow_jump(inst.argval)

        if inst.opcode in pop_and_no_jump:
            pop = True
            inst = self.follow_jump(inst.offset + 2)

        return (pop_and_jump if pop else jump_or_pop, inst.offset)

    def optimize_tuple(self, inst: dis.Instruction) -> Optional[Tuple[int, Any, int]]:
        """
        If tuples are loaded with LOAD_CONST or BUILD_TUPLE depends on linenumbers.
        This function performes this optimization independent of the line numbers.
        """
        if inst.opcode == opcodes.LOAD_CONST and not sys.version_info >= (3, 10):
            values = []
            while inst.opcode in (opcodes.LOAD_CONST, opcodes.EXTENDED_ARG):
                if inst.opcode == opcodes.LOAD_CONST:
                    values.append(inst.argval)

                if inst.offset // 2 == len(self.instructions):
                    break
                inst = self.instructions[inst.offset // 2 + 1]

            # BUILD_LIST is not 100% correct here but this saves us
            # from performance problems on 3.8 in test_extended_arg()
            # [1,2,3,4,5] would trigger the optimization for every LOAD_CONST,
            # which would lead to a quadratic complexity
            if inst.opcode in (
                opcodes.BUILD_TUPLE,
                opcodes.BUILD_LIST,
            ) and inst.argval == len(values):
                return (opcodes.LOAD_CONST, tuple(values), inst.offset + 2)

        return None


def merge_code_fingerprint(
    code_a: CodeFingerprint, code_b: CodeFingerprint
) -> Iterator[Tuple[InstFingerprint, InstFingerprint]]:
    done = set()
    if code_a.start is None or code_b.start is None:
        return

    todo: List[Tuple[int, int]] = [(code_a.start, code_b.start)]

    while todo:
        a, b = todo.pop()
        inst_a = code_a.graph[a]
        inst_b = code_b.graph[b]
        yield (inst_a, inst_b)
        done.add((a, b))

        if TESTING and inst_a.opcode != inst_b.opcode:  # pragma: no cover
            print("code:")
            for ia, ib in zip(code_a.instructions, code_b.instructions):
                print(
                    ia.offset,
                    ia.opname.ljust(20),
                    "==" if ia.opname == ib.opname else "!=",
                    ib.opname,
                )

        assert inst_a.opcode == inst_b.opcode, (inst_a, inst_b)

        todo += [key for key in zip_all(inst_a.next, inst_b.next) if key not in done]


T1 = TypeVar("T1")
T2 = TypeVar("T2")


def zip_all(a: Sequence[T1], b: Sequence[T2]) -> Iterable[Tuple[T1, T2]]:
    assert len(a) == len(b), "length mismatch"

    return zip(a, b)


class CodeMap:
    def __init__(
        self, original_tree: EnhancedAST, filename: str, *, rewrite: Any = None
    ):
        sys.setrecursionlimit(5000)

        if rewrite is not None:
            original_tree = copy.deepcopy(original_tree)

        index_tree = copy.deepcopy(original_tree)

        self.lineno_map: Dict[int, Optional[int]] = {}
        self.node_map: Dict[int, ast.AST] = {}

        self.instructions: Dict[CodeType, List[dis.Instruction]] = {}

        # add index to every node
        for index, (index_node, original_node) in enumerate(
            zip(ast.walk(index_tree), ast.walk(original_tree))
        ):
            assert type(index_node) == type(original_node)

            start_index = index * 2
            end_index = start_index + 1

            if hasattr(index_node, "lineno"):
                assert index_node.lineno == original_node.lineno

                self.lineno_map[start_index] = index_node.lineno
                self.lineno_map[end_index] = index_node.end_lineno

                self.node_map[start_index] = original_node
                self.node_map[end_index] = original_node

                index_node.lineno = start_index
                index_node.end_lineno = end_index
                index_node.col_offset = 0
                index_node.end_col_offset = 0

        # rewrite the ast in the same way some other tools do (pytest for example)
        if rewrite is not None:
            rewrite(index_tree)
            rewrite(original_tree)

        # compile the code
        # the inst.starts_line contains now the index
        original_bc = compile(
            cast(ast.Module, original_tree), filename, "exec", dont_inherit=True
        )
        index_bc = compile(
            cast(ast.Module, index_tree), filename, "exec", dont_inherit=True
        )

        # create a code map where every code-block can be found
        # key is not unique but a good heuristic to speed up the search
        self.code_map: Dict[CodeType, List[Match]] = defaultdict(list)

        self.code_key_cache: Dict[CodeType, CodeFingerprint] = {}

        self.todo: Dict[int, List[Tuple[CodeType, CodeType]]] = defaultdict(list)
        self.todo[original_bc.co_firstlineno] = [(original_bc, index_bc)]

        self.code_lines: Set[int] = set()

    def handle(self, line: int) -> None:
        while line in self.todo or line not in self.code_lines:
            parent_line = max(l for l in self.todo if l <= line)

            for original_code, index_code in self.todo.pop(parent_line):
                original_key = CodeFingerprint(original_code)
                index_key = CodeFingerprint(index_code, lineno_map=self.lineno_map.get)

                offset_to_index = {}

                for original_instr, index_instr in merge_code_fingerprint(
                    original_key, index_key
                ):
                    if index_instr.index is not None:
                        # TODO: why None
                        offset_to_index[original_instr.offset] = index_instr.index

                    if isinstance(original_instr.value, CodeType):
                        assert isinstance(index_instr.value, CodeType)
                        self.todo[original_instr.value.co_firstlineno].append(
                            (original_instr.value, index_instr.value)
                        )

                original_instructions = original_key.instructions

                nodes = [
                    None
                    if inst.offset not in offset_to_index
                    else self.node_map[offset_to_index[inst.offset]]
                    for inst in original_instructions
                ]

                match = Match(nodes, original_code, index_code)

                self.code_map[original_code].append(match)
                self.instructions[original_code] = original_instructions

                self.code_lines.add(original_code.co_firstlineno)

    def __getitem__(self, code: CodeType) -> Tuple[List[Match], List[dis.Instruction]]:
        self.handle(code.co_firstlineno)

        if code in self.code_map:
            return self.code_map[code], self.instructions[code]
        else:
            # this code tries to find code which contains nan (not a number) in the co_consts
            # of the code object
            # nan or something which contains nan (like code objects) can not be used
            # as key for a dict lookup, because `nan != nan`

            # performance is not so important here because this case is really unlikely
            code_key = normalize(code)
            for key, value in self.code_map.items():
                if normalize(key) == code_key:
                    return (value, self.instructions[key])

        return ([], [])


def is_module_rewritten_by_pytest(frame: FrameType) -> bool:
    global_vars = frame.f_globals.keys()
    return "@py_builtins" in global_vars or "@pytest_ar" in global_vars


class IndexNodeFinder(BaseNodeFinder):
    """
    Mapping bytecode to ast-node based on the source positions, which where introduced in pyhon 3.11.
    In general every ast-node can be exactly referenced by its begin/end line/col_offset, which is stored in the bytecode.
    There are only some exceptions for methods and attributes.
    """

    @staticmethod
    @lru_cache(100)
    def get_code_map(tree: EnhancedAST, filename: str) -> CodeMap:
        return CodeMap(tree, filename)

    @staticmethod
    @lru_cache(100)
    def get_code_map_pytest(tree: EnhancedAST, filename: str, text: str) -> CodeMap:
        return CodeMap(
            tree, filename, rewrite=lambda tree: pytest_rewrite_assert(tree, text)
        )

    def __init__(
        self,
        frame: FrameType,
        stmts: Set[EnhancedAST],
        tree: ast.Module,
        lasti: int,
        source: Source,
    ):
        # maybe pytest has rewritten the assertions
        if is_module_rewritten_by_pytest(frame):
            code_map = self.get_code_map_pytest(tree, source.text, source.filename)
        else:
            code_map = self.get_code_map(tree, source.filename)

            # lookup the current frame in the code_map
        matches, instructions = code_map[frame.f_code]

        if not matches:  # pragma: no cover
            raise NotOneValueFound("no match found")

        while instructions[lasti // 2].opcode == opcodes.EXTENDED_ARG:
            lasti += 2
        instruction = instructions[lasti // 2]

        if len(matches) == 1:
            match = matches[0]
        else:
            # in code for this generator expression ends up twice in the bytecode
            # might be a bug
            # while (t for t in s):
            #     pass

            if all_equal(m.index_code for m in matches):
                match = matches[0]
            else:
                nodes = [
                    self.get_node(match, instructions, lasti, tree)[0]
                    for match in matches
                ]
                raise MultipleMatches(nodes)

        if instructions[lasti // 2].opcode == opcodes.NOP:
            raise KnownIssue("can not map NOP")

        self.result, self.decorator = self.get_node(match, instructions, lasti, tree)

        self.known_issues(self.result, instruction, instructions, frame.f_code.co_name)

        if self.decorator is None:
            self.verify(self.result, instruction)
        else:
            assert_(self.decorator in cast(ast.FunctionDef, self.result).decorator_list)

    def known_issues(
        self,
        node: EnhancedAST,
        instruction: dis.Instruction,
        instructions: List[dis.Instruction],
        co_name: str,
    ) -> None:
        inst_index = instruction.offset // 2

        # known issues
        if self.is_except_cleanup(instruction, node):
            raise KnownIssue(
                "exeption cleanup does not belong to the last node in a except block"
            )

        if sys.version_info >= (3, 10) and isinstance(self.result, ast.pattern):
            raise KnownIssue("there are some wired bugs in pattern locations")

        if isinstance(self.result, ast.Assert):
            raise KnownIssue("assert matched")

        compare_opcodes = (
            (opcodes.COMPARE_OP, opcodes.CONTAINS_OP, opcodes.IS_OP)
            if sys.version_info >= (3, 9)
            else (opcodes.COMPARE_OP,)
        )

        if instruction.opcode in compare_opcodes and not isinstance(node, ast.Compare):
            raise KnownIssue("COMPARE_OP seems broken")

        if (
            sys.version_info >= (3, 8)
            and not sys.version_info >= (3, 9)
            and instruction.opcode in (opcodes.CALL_FINALLY,)
        ):
            raise KnownIssue("CALL_FINALLY seems broken")

        if (
            sys.version_info >= (3, 8)
            and not sys.version_info >= (3, 9)
            and instruction.opcode in (opcodes.WITH_CLEANUP_START,)
        ):
            raise KnownIssue("call to __exit__ can not be mapped")

        if (
            sys.version_info >= (3, 9)
            and not sys.version_info >= (3, 10)
            and instruction.opcode == opcodes.CALL_FUNCTION
            and not isinstance(node, ast.Call)
            and not isinstance(node, (ast.With, ast.AsyncWith))
            and has_parent(node, (ast.With, ast.AsyncWith))
        ):
            # __exit__ can not be mapped

            patterns = [
                [
                    opcodes.POP_BLOCK,
                    opcodes.LOAD_CONST,
                    opcodes.DUP_TOP,
                    opcodes.DUP_TOP,
                    opcodes.CALL_FUNCTION,
                ],
                [
                    opcodes.POP_BLOCK,
                    opcodes.ROT_TWO,
                    opcodes.LOAD_CONST,
                    opcodes.DUP_TOP,
                    opcodes.DUP_TOP,
                    opcodes.CALL_FUNCTION,
                ],
            ]
            for pattern in patterns:
                if inst_index >= len(pattern) - 1:
                    exit_instructions = [
                        i.opcode
                        for i in instructions[: inst_index + 1]
                        if i.opcode != opcodes.EXTENDED_ARG
                    ][-len(pattern) :]
                    if exit_instructions == pattern:
                        raise KnownIssue("call to __exit__ can not be mapped")

        if (
            # todo find correct version
            sys.version_info[:2] == (3, 10)
            and isinstance(node, ast.Compare)
            and instruction.opcode == opcodes.CALL_FUNCTION
            and any(isinstance(n, ast.Assert) for n in node_and_parents(node))
        ):
            raise KnownIssue(
                "known bug in 3.11.1 https://github.com/python/cpython/issues/95921"
            )

        if self.in_class_prelog(
            instructions, co_name, instruction.offset
        ) and not isinstance(node, ast.ClassDef):
            raise KnownIssue(
                "header of class with decorators has wrong source positions"
            )

        if (
            instruction.opcode == opcodes.STORE_NAME
            and instruction.argval == "__classcell__"
        ):
            raise KnownIssue("store __classcell__")

    def get_node(
        self,
        match: Match,
        instructions: List[dis.Instruction],
        lasti: int,
        tree: ast.Module,
    ) -> Tuple[EnhancedAST, Union[ast.AST, None]]:
        index = lasti // 2

        result = match.nodes[index]
        decorator = None

        instruction = instructions[index]

        if result is None:
            if instruction.opcode in (opcodes.NOP, opcodes.JUMP_ABSOLUTE):
                raise KnownIssue("%s can not be mapped" % instruction.opname)
            else:
                raise NotOneValueFound("could not match %s" % instruction.opname)

        # workaround for method calls
        # thing.method()
        #     ^ end_lineno
        # end_lineno of the attribute is used by the python compiler
        # for the linenumber of the CALL and CALL_METHOD instruction
        # !!! the same end_lineno is used for starts_line of `thing`
        if sys.version_info >= (3, 10):
            if instructions[lasti // 2].opcode == opcodes.CALL_METHOD:
                if not isinstance(result, ast.JoinedStr):
                    assert isinstance(result.parent, ast.Call), (result, result.parent)
                    result = result.parent

        elif (
            sys.version_info >= (3, 8)
            and instructions[lasti // 2].opcode == opcodes.LOAD_METHOD
            and isinstance(result, ast.Call)
        ):
            result = result.func

        # detecting decorators
        index = lasti // 2
        if (
            isinstance(result, (ast.ClassDef, function_node_types))
            and instructions[index].opcode == opcodes.CALL_FUNCTION
        ):
            decorator_index = 0
            while instructions[index].opcode == opcodes.CALL_FUNCTION:
                index += 1
                while instructions[index].opcode == opcodes.EXTENDED_ARG:
                    index += 1

                decorator_index += 1
            decorator_index -= 1
            if 0 <= decorator_index < len(result.decorator_list) and instructions[
                index
            ].opname.startswith("STORE_"):
                decorator = result.decorator_list[decorator_index]

        return result, decorator

    def in_class_prelog(
        self, instructions: List[dis.Instruction], code_name: str, offset: int
    ) -> bool:
        prelog = [
            (0, opcodes.LOAD_NAME, "__name__"),
            (2, opcodes.STORE_NAME, "__module__"),
            (4, opcodes.LOAD_CONST, code_name),
            (6, opcodes.STORE_NAME, "__qualname__"),
        ]
        code_start = [
            (
                instruction.offset,
                instruction.opcode,
                isinstance(instruction.argval, str)
                and instruction.argval.split(".")[-1],
            )
            for instruction in instructions[: len(prelog)]
        ]

        return prelog == code_start and offset // 2 < len(prelog)
