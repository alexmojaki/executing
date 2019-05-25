import __future__
import ast
import dis
import inspect
import sys
from collections import defaultdict, namedtuple, Sized
from contextlib import contextmanager
from itertools import islice
from threading import RLock

PY3 = sys.version_info[0] == 3

if PY3:
    # noinspection PyUnresolvedReferences
    from functools import lru_cache

    cache = lru_cache()
else:
    def cache(f):
        """ Memoization decorator for a function taking a single argument """

        class MemoDict(dict):
            def __missing__(self, key):
                ret = self[key] = f(key)
                return ret

        return MemoDict().__getitem__

try:
    # noinspection PyUnresolvedReferences
    get_instructions = dis.get_instructions
except AttributeError:
    Instruction = namedtuple('Instruction', 'offset argval opname')


    def to_int(c):
        if isinstance(c, int):
            return c
        else:
            return ord(c)


    def get_instructions(co):
        code = co.co_code
        n = len(code)
        i = 0
        extended_arg = 0
        while i < n:
            offset = i
            op = to_int(code[i])
            opname = dis.opname[op]
            argval = None
            i = i + 1
            if op >= dis.HAVE_ARGUMENT:
                oparg = to_int(code[i]) + to_int(code[i + 1]) * 256 + extended_arg
                extended_arg = 0
                i = i + 2
                if op == dis.EXTENDED_ARG:
                    extended_arg = oparg * 65536

                if op in dis.hasconst:
                    argval = co.co_consts[oparg]
            yield Instruction(offset, argval, opname)


def only(it):
    """
    >>> only([7])
    7
    >>> only([1, 2])
    Traceback (most recent call last):
    ...
    AssertionError: Expected one value, found 2
    >>> only([])
    Traceback (most recent call last):
    ...
    AssertionError: Expected one value, found 0
    >>> from itertools import repeat
    >>> only(repeat(5))
    Traceback (most recent call last):
    ...
    AssertionError: Expected one value, found several
    >>> only(repeat(5, 0))
    Traceback (most recent call last):
    ...
    AssertionError: Expected one value, found 0
    """

    if isinstance(it, Sized):
        if len(it) != 1:
            raise AssertionError('Expected one value, found %s' % len(it))
        # noinspection PyTypeChecker
        return list(it)[0]

    lst = tuple(islice(it, 2))
    if len(lst) == 0:
        raise AssertionError('Expected one value, found 0')
    if len(lst) > 1:
        raise AssertionError('Expected one value, found several')
    return lst[0]


class FileInfo(object):
    """
    Contains metadata about a python source file:

        - path: path to the file
        - source: text contents of the file
        - tree: AST parsed from the source
        - asttokens(): ASTTokens object for getting the source of specific AST nodes
        - nodes_by_lines: dictionary from line numbers
            to a list of AST nodes at that line

    Each node in the AST has an extra attribute 'parent'.

    Users should not need to create instances of this class themselves.
    This class should not be instantiated directly, rather use file_info for caching.
    """

    def __init__(self, path):
        with open(path) as f:
            self.source = f.read()
        self.tree = ast.parse(self.source, filename=path)
        self.nodes_by_line = defaultdict(list)
        for node in ast.walk(self.tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node
            if hasattr(node, 'lineno'):
                self.nodes_by_line[node.lineno].append(node)
        self.path = path

    @staticmethod
    def for_frame(frame):
        return file_info(frame.f_code.co_filename)

    def _call_at(self, frame):
        stmts = {
            statement_containing_node(node)
            for node in
            self.nodes_by_line[frame.f_lineno]
        }
        return CallFinder(frame, stmts).result


file_info = cache(FileInfo)

sentinel = 'io8urthglkjdghvljusketgIYRFYUVGHFRTBGVHKGF78678957647698'

special_code_names = ('<listcomp>', '<dictcomp>', '<setcomp>', '<lambda>', '<genexpr>')

future_flags = sum(
    getattr(__future__, fname).compiler_flag
    for fname in __future__.all_feature_names
)


class CallFinder(object):
    def __init__(self, frame, stmts):
        self.frame = frame
        a_stmt = self.a_stmt = list(stmts)[0]
        body = self.body = only(
            lst
            for lst in get_node_bodies(a_stmt.parent)
            if a_stmt in lst
        )
        stmts = self.stmts = sorted(stmts, key=body.index)
        self.sandbox_module = self.make_sandbox_module()
        call_instruction_index = self.get_call_instruction_index()

        calls = [
            node
            for stmt in stmts
            for node in ast.walk(stmt)
            if isinstance(node, ast.Call)
        ]

        for i, call in enumerate(calls):
            with add_sentinel_kwargs(call):
                ast.fix_missing_locations(call)
                instructions = self.compile_instructions()

            indices = [
                i
                for i, instruction in enumerate(instructions)
                if instruction.argval == sentinel
            ]
            if not indices:
                continue
            arg_index = only(indices)
            new_instruction = _call_instructions(instructions[arg_index:])[0]

            call_instructions = _call_instructions(instructions)
            new_instruction_index = only(
                i
                for i, instruction in enumerate(call_instructions)
                if instruction is new_instruction
            )

            if new_instruction_index == call_instruction_index:
                self.result = call
                break

    def get_call_instruction_index(self):
        frame_offset_relative_to_stmt = self.frame.f_lasti
        if self.frame.f_code.co_name not in special_code_names:
            frame_offset_relative_to_stmt -= self.stmt_offset()
        instruction_index = only(
            i
            for i, instruction in enumerate(_call_instructions(self.compile_instructions()))
            if instruction.offset == frame_offset_relative_to_stmt
        )
        return instruction_index

    def make_sandbox_module(self):
        function = ast.FunctionDef(
            name='<function>',
            body=self.stmts,
            args=ast.arguments(args=[], kwonlyargs=[], kw_defaults=[], defaults=[]),
            decorator_list=[],
        )
        ast.copy_location(function, self.stmts[0])
        return ast.Module(body=[function])

    def stmt_offset(self):
        body = self.body
        stmts = self.stmts
        a_stmt = self.a_stmt

        stmt_index = body.index(stmts[0])
        expr = ast.Expr(
            value=ast.List(
                elts=[ast.Str(s=sentinel)],
                ctx=ast.Load(),
            ),
        )
        with tweak_list(body):
            body.insert(stmt_index, expr)
            ast.copy_location(expr, stmts[0])
            ast.fix_missing_locations(a_stmt.parent)

            parent_block = get_containing_block(a_stmt)
            if isinstance(parent_block, ast.Module):
                assert self.frame.f_code.co_name == '<module>'
                module = parent_block
                extract = False
            else:
                module = ast.Module(body=[parent_block])
                extract = True
            instructions = self._stmt_instructions(module, extract=extract)

            return only(
                instruction
                for instruction in instructions
                if instruction.argval == sentinel
            ).offset

    def compile_instructions(self):
        return self._stmt_instructions(self.sandbox_module, matching_code=self.frame.f_code)

    def _stmt_instructions(self, module, matching_code=None, extract=True):
        flags = self.frame.f_code.co_flags & future_flags
        code = compile(module, '<mod>', 'exec', flags=flags, dont_inherit=True)
        if extract:
            stmt_code = only(
                c
                for c in code.co_consts
                if inspect.iscode(c)
            )
            code = find_code(stmt_code, matching_code)
        return list(get_instructions(code))


lock = RLock()


@contextmanager
def tweak_list(lst):
    with lock:
        original = lst[:]
        try:
            yield
        finally:
            lst[:] = original


if sys.version_info[:2] >= (3, 5):
    @contextmanager
    def add_sentinel_kwargs(call):
        keyword = ast.keyword(arg=None, value=ast.Str(s=sentinel))
        with lock:
            with tweak_list(call.keywords):
                call.keywords.append(keyword)
                yield
else:
    @contextmanager
    def add_sentinel_kwargs(call):
        with lock:
            original = call.kwargs
            call.kwargs = ast.Str(s=sentinel)
            try:
                yield
            finally:
                call.kwargs = original


def get_node_bodies(node):
    for name, field in ast.iter_fields(node):
        if isinstance(field, list):
            yield field


def get_containing_block(node):
    while True:
        node = node.parent
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef)):
            return node


def _call_instructions(instructions):
    return [
        instruction
        for instruction in instructions
        if instruction.opname.startswith(('CALL_FUNCTION', 'CALL_METHOD'))
    ]


def find_code(root_code, matching):
    if matching is None or matching.co_name not in special_code_names:
        return root_code

    code_options = []

    def finder(code):
        for const in code.co_consts:
            if not inspect.iscode(const):
                continue
            matches = (const.co_firstlineno == matching.co_firstlineno and
                       const.co_name == matching.co_name)
            if matches:
                code_options.append(const)
            finder(const)

    finder(root_code)
    return only(code_options)


@cache
def statement_containing_node(node):
    while not isinstance(node, ast.stmt):
        node = node.parent
    return node


def executing_node(frame):
    return FileInfo.for_frame(frame)._call_at(frame)
