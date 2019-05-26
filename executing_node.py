import ast
import dis
import functools
import inspect
import io
import linecache
import sys
from collections import defaultdict, namedtuple, Sized
from contextlib import contextmanager
from itertools import islice
from operator import attrgetter
from threading import RLock

PY3 = sys.version_info[0] == 3

if PY3:
    # noinspection PyUnresolvedReferences
    from functools import lru_cache
    # noinspection PyUnresolvedReferences
    from tokenize import detect_encoding

    cache = lru_cache()
    text_type = str
else:
    from lib2to3.pgen2.tokenize import detect_encoding


    def cache(func):
        d = {}

        @functools.wraps(func)
        def wrapper(*args):
            if args in d:
                return d[args]
            result = d[args] = func(*args)
            return result

        return wrapper


    text_type = unicode
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


class NotOneValueFound(Exception):
    pass


class SourceNotFoundException(Exception):
    pass


try:
    # noinspection PyUnresolvedReferences
    from IPython import get_ipython


    def ipython_flags():
        shell = get_ipython()
        if shell:
            return shell.compile.flags
        else:
            return 0
except ImportError:
    def ipython_flags():
        return 0


def only(it):
    if isinstance(it, Sized):
        if len(it) != 1:
            raise NotOneValueFound('Expected one value, found %s' % len(it))
        # noinspection PyTypeChecker
        return list(it)[0]

    lst = tuple(islice(it, 2))
    if len(lst) == 0:
        raise NotOneValueFound('Expected one value, found 0')
    if len(lst) > 1:
        raise NotOneValueFound('Expected one value, found several')
    return lst[0]


source_cache = {}
_executing_cache = {}


class Source(object):
    def __init__(self, module_name, filename, text):
        self.module_name = module_name
        self.filename = filename
        self.text = text
        self.tree = ast.parse(text, filename=filename)
        self.nodes_by_line = defaultdict(list)
        for node in ast.walk(self.tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node
            if hasattr(node, 'lineno'):
                self.nodes_by_line[node.lineno].append(node)

    @classmethod
    def for_frame(cls, frame):
        globs = frame.f_globals or {}
        module_name = globs.get('__name__')
        filename = frame.f_code.co_filename
        cache_key = (module_name, filename)

        try:
            return source_cache[cache_key]
        except KeyError:
            pass

        text = None

        try:
            text = globs['__loader__'].get_source(module_name)
        except Exception:
            pass

        if text is None:
            try:
                text = ''.join(linecache.cache[filename][2])
            except KeyError:
                pass

        if text is None:
            try:
                with open(filename, 'rb') as fp:
                    text = fp.read()
            except (IOError, OSError):
                pass

        if text is None:
            raise SourceNotFoundException(
                "Couldn't find source for %s - %s"
                % (module_name, filename)
            )

        if isinstance(text, bytes):
            encoding, _ = detect_encoding(io.BytesIO(text).readline)
            text = text_type(text, encoding, 'replace')

        text = source_cache[cache_key] = cls(module_name, filename, text)
        return text

    @classmethod
    def executing_node(cls, frame):
        key = (frame.f_code, frame.f_lasti)
        try:
            return _executing_cache[key]
        except KeyError:
            pass

        tree = cls.for_frame(frame).tree
        stmts = cls.executing_statements(frame)
        result = _executing_cache[key] = CallFinder(frame, stmts, tree).result
        return result

    @classmethod
    def executing_statements(cls, frame):
        return cls.for_frame(frame)._statements_at(frame.f_lineno)

    @cache
    def _statements_at(self, lineno):
        stmts_set = {
            statement_containing_node(node)
            for node in
            self.nodes_by_line[lineno]
        }
        a_stmt = list(stmts_set)[0]
        body = only(
            lst
            for lst in get_node_bodies(a_stmt.parent)
            if a_stmt in lst
        )
        return sorted(stmts_set, key=body.index)

    @cache
    def asttokens(self):
        """
        Returns an ASTTokens object for getting the source of specific AST nodes.

        See http://asttokens.readthedocs.io/en/latest/api-index.html
        """
        from asttokens import ASTTokens
        return ASTTokens(
            self.text,
            tree=self.tree,
            filename=self.filename,
        )


sentinel = 'io8urthglkjdghvljusketgIYRFYUVGHFRTBGVHKGF78678957647698'


class CallFinder(object):
    def __init__(self, frame, stmts, tree):
        self.frame = frame
        self.tree = tree
        call_instruction_index = only(
            i
            for i, instruction in enumerate(
                _call_instructions(self.compile_instructions()))
            if instruction.offset == self.frame.f_lasti
        )

        calls = [
            node
            for stmt in stmts
            for node in ast.walk(stmt)
            if isinstance(node, ast.Call)
        ]

        self.result = only(self.matching_calls(calls, call_instruction_index))

    def matching_calls(self, calls, call_instruction_index):
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
                yield call

    def compile_instructions(self):
        module_code = compile(
            self.tree,
            '<mod>',
            'exec',
            flags=ipython_flags(),
            dont_inherit=True,
        )
        code = find_code(module_code, self.frame.f_code)
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


def _call_instructions(instructions):
    return [
        instruction
        for instruction in instructions
        if instruction.opname.startswith(('CALL_FUNCTION', 'CALL_METHOD'))
    ]


def find_code(root_code, matching):
    def matches(c):
        return all(
            f(c) == f(matching)
            for f in [
                attrgetter('co_firstlineno'),
                attrgetter('co_name'),
                code_names,
            ]
        )

    code_options = []
    if matches(root_code):
        code_options.append(root_code)

    def finder(code):
        for const in code.co_consts:
            if not inspect.iscode(const):
                continue

            if matches(const):
                code_options.append(const)
            finder(const)

    finder(root_code)
    return only(code_options)


def code_names(code):
    return frozenset().union(
        code.co_names,
        code.co_varnames,
        code.co_freevars,
        code.co_cellvars,
    )


@cache
def statement_containing_node(node):
    while not isinstance(node, ast.stmt):
        node = node.parent
    return node
