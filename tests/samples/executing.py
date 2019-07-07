"""
Get information about what a frame is currently doing. Typical usage:

    import executing

    node = executing.Source.executing(frame).node
    # node will be an AST node or None
"""

import __future__
import ast
import dis
import functools
import inspect
import io
import linecache
import sys
from collections import defaultdict, namedtuple, Sized
from itertools import islice
from lib2to3.pgen2.tokenize import cookie_re as encoding_pattern
from operator import attrgetter
from threading import RLock

__all__ = ["Source"]

PY3 = sys.version_info[0] == 3

if PY3:
    # noinspection PyUnresolvedReferences
    from functools import lru_cache
    # noinspection PyUnresolvedReferences
    from tokenize import detect_encoding

    cache = lru_cache(maxsize=None)
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


    # noinspection PyUnresolvedReferences
    text_type = unicode
try:
    # noinspection PyUnresolvedReferences
    get_instructions = dis.get_instructions
except AttributeError:
    Instruction = namedtuple('Instruction', 'offset argval opname')

    from dis import HAVE_ARGUMENT, EXTENDED_ARG, hasconst, opname

    # Based on dis.disassemble from 2.7
    # Left as similar as possible for easy diff

    def get_instructions(co):
        code = co.co_code
        n = len(code)
        i = 0
        extended_arg = 0
        while i < n:
            offset = i
            c = code[i]
            op = ord(c)
            argval = None
            i = i + 1
            if op >= HAVE_ARGUMENT:
                oparg = ord(code[i]) + ord(code[i + 1]) * 256 + extended_arg
                extended_arg = 0
                i = i + 2
                if op == EXTENDED_ARG:
                    extended_arg = oparg * 65536

                if op in hasconst:
                    argval = co.co_consts[oparg]
            yield Instruction(offset, argval, opname[op])


class NotOneValueFound(Exception):
    pass


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


class Source(object):
    """
    The source code of a single file and associated metadata.

    The main method of interest is the classmethod `executing(frame)`.

    If you want an instance of this class, don't construct it.
    Ideally use the classmethod `for_frame(frame)`.
    If you don't have a frame, use `for_filename(filename [, module_globals])`.
    These methods cache instances by filename, so at most one instance exists per filename.

    Attributes:
        - filename
        - text
        - tree: AST parsed from text, or None if text is not valid Python
            All nodes in the tree have an extra `parent` attribute

    Other methods of interest:
        - statements_at_line
        - asttokens
        - code_qualname
    """

    def __init__(self, filename, text):
        """
        Don't call this constructor, see the class docstring.
        """

        self.filename = filename

        if not isinstance(text, text_type):
            text = self.decode_source(text)
        self.text = text

        if PY3:
            ast_text = text
        else:
            # In python 2 it's a syntax error to parse unicode
            # with an encoding declaration, so we remove it but
            # leave empty lines in its place to keep line numbers the same
            ast_text = ''.join([
                '\n' if i < 2 and encoding_pattern.match(line)
                else line
                for i, line in enumerate(text.splitlines(True))
            ])

        self._nodes_by_line = defaultdict(list)
        self.tree = None
        self._qualnames = {}

        if text:
            try:
                self.tree = ast.parse(ast_text, filename=filename)
            except SyntaxError:
                pass
            else:
                for node in ast.walk(self.tree):
                    for child in ast.iter_child_nodes(node):
                        child.parent = node
                    if hasattr(node, 'lineno'):
                        self._nodes_by_line[node.lineno].append(node)

                visitor = QualnameVisitor()
                visitor.visit(self.tree)
                self._qualnames = visitor.qualnames

    @classmethod
    def for_frame(cls, frame):
        """
        Returns the `Source` object corresponding to the file the frame is executing in.
        """
        return cls.for_filename(frame.f_code.co_filename, frame.f_globals or {})

    @classmethod
    def for_filename(cls, filename, module_globals=None):
        source_cache = cls._class_local('__source_cache', {})
        try:
            return source_cache[filename]
        except KeyError:
            pass

        lines = linecache.getlines(filename, module_globals)
        result = source_cache[filename] = cls(filename, ''.join(lines))
        return result

    @classmethod
    def lazycache(cls, frame):
        if hasattr(linecache, 'lazycache'):
            linecache.lazycache(frame.f_code.co_filename, frame.f_globals)

    @classmethod
    def executing(cls, frame):
        """
        Returns an `Executing` object representing the operation
        currently executing in the given frame.
        """
        key = (frame.f_code, frame.f_lasti)
        executing_cache = cls._class_local('__executing_cache', {})

        try:
            args = executing_cache[key]
        except KeyError:
            source = cls.for_frame(frame)
            node = stmts = None
            if source.tree:
                stmts = source.statements_at_line(frame.f_lineno)
                try:
                    node = NodeFinder(frame, stmts, source.tree).result
                except Exception:
                    raise
                else:
                    new_stmts = {statement_containing_node(node)}
                    assert new_stmts <= stmts
                    stmts = new_stmts

            args = source, node, stmts
            executing_cache[key] = args

        return Executing(frame, *args)

    @classmethod
    def _class_local(cls, name, default):
        """
        Returns an attribute directly associated with this class
        (as opposed to subclasses), setting default if necessary
        """
        # classes have a mappingproxy preventing us from using setdefault
        result = cls.__dict__.get(name, default)
        setattr(cls, name, result)
        return result

    @cache
    def statements_at_line(self, lineno):
        """
        Returns the statement nodes overlapping the given line.

        Returns at most one statement unless semicolons are present.

        If the `text` attribute is not valid python, meaning
        `tree` is None, returns an empty set.

        Otherwise, `Source.for_frame(frame).statements_at_line(frame.f_lineno)`
        should return at least one statement.
        """

        return {
            statement_containing_node(node)
            for node in
            self._nodes_by_line[lineno]
        }

    @cache
    def asttokens(self):
        """
        Returns an ASTTokens object for getting the source of specific AST nodes.

        See http://asttokens.readthedocs.io/en/latest/api-index.html
        """
        from asttokens import ASTTokens  # must be installed separately
        return ASTTokens(
            self.text,
            tree=self.tree,
            filename=self.filename,
        )

    @staticmethod
    def decode_source(source):
        if isinstance(source, bytes):
            encoding, _ = detect_encoding(io.BytesIO(source).readline)
            source = source.decode(encoding)
        return source

    def code_qualname(self, code):
        """
        Imitates the __qualname__ attribute of functions for code objects.
        Given:

            - A function `func`
            - A frame `frame` for an execution of `func`, meaning:
                `frame.f_code is func.__code__`

        `Source.for_frame(frame).code_qualname(frame.f_code)`
        will be equal to `func.__qualname__`*. Works for Python 2 as well,
        where of course no `__qualname__` attribute exists.

        Falls back to `code.co_name` if there is no appropriate qualname.

        Based on https://github.com/wbolster/qualname

        (* unless `func` is a lambda
        nested inside another lambda on the same line, in which case
        the outer lambda's qualname will be returned for the codes
        of both lambdas)
        """
        assert code.co_filename == self.filename
        return self._qualnames.get((code.co_name, code.co_firstlineno), code.co_name)


class Executing(object):
    """
    Information about the operation a frame is currently executing.

    Generally you will just want `node`, which is the AST node being executed,
    or None if it's unknown.
    Currently `node` can only be an `ast.Call` object, other operations
    will be supported in future.
    """

    def __init__(self, frame, source, node, stmts):
        self.frame = frame
        self.source = source
        self.node = node
        self.statements = stmts

    def code_qualname(self):
        return self.source.code_qualname(self.frame.f_code)

    def text(self):
        return self.source.asttokens().get_text(self.node)

    def text_range(self):
        return self.source.asttokens().get_text_range(self.node)


class QualnameVisitor(ast.NodeVisitor):
    def __init__(self):
        super(QualnameVisitor, self).__init__()
        self.stack = []
        self.qualnames = {}

    def visit_FunctionDef(self, node, name=None):
        name = name or node.name
        self.stack.append(name)
        self.qualnames.setdefault((name, node.lineno), ".".join(self.stack))

        self.stack.append('<locals>')
        if isinstance(node, ast.Lambda):
            children = [node.body]
        else:
            children = node.body
        for child in children:
            self.visit(child)
        self.stack.pop()
        self.stack.pop()

        # Find lambdas in the function definition outside the body,
        # e.g. decorators or default arguments
        # Based on iter_child_nodes
        for field, child in ast.iter_fields(node):
            if field == 'body':
                continue
            if isinstance(child, ast.AST):
                self.visit(child)
            elif isinstance(child, list):
                for grandchild in child:
                    if isinstance(grandchild, ast.AST):
                        self.visit(grandchild)

    def visit_Lambda(self, node):
        self.visit_FunctionDef(node, '<lambda>')

    def visit_ClassDef(self, node):
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()


future_flags = sum(
    getattr(__future__, fname).compiler_flag
    for fname in __future__.all_feature_names
)


def compile_similar_to(source, matching_code):
    return compile(
        source,
        matching_code.co_filename,
        'exec',
        flags=future_flags & matching_code.co_flags,
        dont_inherit=True,
    )


sentinel = ''


class NodeFinder(object):
    def __init__(self, frame, stmts, tree):
        self.frame = frame
        self.tree = tree

        b = frame.f_code.co_code[frame.f_lasti]
        if not PY3:
            b = ord(b)
        op_name = dis.opname[b]

        if op_name.startswith('CALL_'):
            typ = ast.Call
        elif op_name == 'BINARY_SUBSCR':
            typ = ast.Subscript
        elif op_name.startswith('BINARY_'):
            typ = ast.BinOp
        elif op_name.startswith('UNARY_'):
            typ = ast.UnaryOp
        elif op_name in ('LOAD_ATTR', 'LOAD_METHOD', 'LOOKUP_METHOD'):
            typ = ast.Attribute
        elif op_name == 'COMPARE_OP':
            typ = ast.Compare
        else:
            raise RuntimeError(op_name)

        with lock:
            exprs = {
                node
                for stmt in stmts
                for node in ast.walk(stmt)
                if isinstance(node, typ)
                if not (hasattr(node, "ctx") and not isinstance(node.ctx, ast.Load))
            }

            self.result = only(list(self.matching_nodes(exprs)))

    def matching_nodes(self, exprs):
        for i, expr in enumerate(exprs):
            setter = get_setter(expr)
            replacement = ast.BinOp(
                left=expr,
                op=ast.Pow(),
                right=ast.Str(s=sentinel),
            )
            ast.fix_missing_locations(replacement)
            setter(replacement)
            try:
                instructions = self.compile_instructions()
            except SyntaxError:
                continue
            finally:
                setter(expr)
            indices = [
                i
                for i, instruction in enumerate(instructions)
                if instruction.argval == sentinel
            ]
            if not indices:
                continue
            arg_index = only(indices) - 1
            while instructions[arg_index].opname == 'EXTENDED_ARG':
                arg_index -= 1

            if instructions[arg_index].offset == self.frame.f_lasti:
                yield expr

    def compile_instructions(self):
        module_code = compile_similar_to(self.tree, self.frame.f_code)
        code = only(find_codes(module_code, self.frame.f_code))
        return list(get_instructions(code))


def get_setter(node):
    parent = node.parent
    for name, field in ast.iter_fields(parent):
        if field is node:
            return lambda new_node: setattr(parent, name, new_node)
        elif isinstance(field, list):
            for i, item in enumerate(field):
                if item is node:
                    def setter(new_node):
                        field[i] = new_node

                    return setter


lock = RLock()


def find_codes(root_code, matching):
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
    return code_options


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
