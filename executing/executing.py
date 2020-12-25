import __future__
import ast
import dis
import functools
import inspect
import io
import linecache
import sys
import types
from collections import defaultdict, namedtuple
from itertools import islice
from operator import attrgetter
from threading import RLock

PY3 = sys.version_info[0] == 3

if PY3:
    # noinspection PyUnresolvedReferences
    from functools import lru_cache
    # noinspection PyUnresolvedReferences
    from tokenize import detect_encoding
    from itertools import zip_longest
    # noinspection PyUnresolvedReferences,PyCompatibility
    from pathlib import Path

    cache = lru_cache(maxsize=None)
    text_type = str
else:
    from lib2to3.pgen2.tokenize import detect_encoding, cookie_re as encoding_pattern
    from itertools import izip_longest as zip_longest


    class Path(object):
        pass


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
    _get_instructions = dis.get_instructions
except AttributeError:
    class Instruction(namedtuple('Instruction', 'offset argval opname starts_line')):
        lineno = None


    from dis import HAVE_ARGUMENT, EXTENDED_ARG, hasconst, opname, findlinestarts

    # Based on dis.disassemble from 2.7
    # Left as similar as possible for easy diff

    def _get_instructions(co):
        code = co.co_code
        linestarts = dict(findlinestarts(co))
        n = len(code)
        i = 0
        extended_arg = 0
        while i < n:
            offset = i
            c = code[i]
            op = ord(c)
            lineno = linestarts.get(i)
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
            yield Instruction(offset, argval, opname[op], lineno)


def assert_(condition, message=""):
    """
    Like an assert statement, but unaffected by -O
    :param condition: value that is expected to be truthy
    :type message: Any
    """
    if not condition:
        raise AssertionError(str(message))


def get_instructions(co):
    lineno = None
    for inst in _get_instructions(co):
        lineno = inst.starts_line or lineno
        assert_(lineno)
        inst.lineno = lineno
        yield inst


TESTING = 0


class NotOneValueFound(Exception):
    pass


def only(it):
    if hasattr(it, '__len__'):
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
        - lines
        - tree: AST parsed from text, or None if text is not valid Python
            All nodes in the tree have an extra `parent` attribute

    Other methods of interest:
        - statements_at_line
        - asttokens
        - code_qualname
    """

    def __init__(self, filename, lines):
        """
        Don't call this constructor, see the class docstring.
        """

        self.filename = filename
        text = ''.join(lines)

        if not isinstance(text, text_type):
            encoding = self.detect_encoding(text)
            # noinspection PyUnresolvedReferences
            text = text.decode(encoding)
            lines = [line.decode(encoding) for line in lines]

        self.text = text
        self.lines = [line.rstrip('\r\n') for line in lines]

        if PY3:
            ast_text = text
        else:
            # In python 2 it's a syntax error to parse unicode
            # with an encoding declaration, so we remove it but
            # leave empty lines in its place to keep line numbers the same
            ast_text = ''.join([
                '\n' if i < 2 and encoding_pattern.match(line)
                else line
                for i, line in enumerate(lines)
            ])

        self._nodes_by_line = defaultdict(list)
        self.tree = None
        self._qualnames = {}

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
    def for_frame(cls, frame, use_cache=True):
        """
        Returns the `Source` object corresponding to the file the frame is executing in.
        """
        return cls.for_filename(frame.f_code.co_filename, frame.f_globals or {}, use_cache)

    @classmethod
    def for_filename(cls, filename, module_globals=None, use_cache=True):
        if isinstance(filename, Path):
            filename = str(filename)

        source_cache = cls._class_local('__source_cache', {})
        if use_cache:
            try:
                return source_cache[filename]
            except KeyError:
                pass

        if not use_cache:
            linecache.checkcache(filename)

        lines = tuple(linecache.getlines(filename, module_globals))
        result = source_cache[filename] = cls._for_filename_and_lines(filename, lines)
        return result

    @classmethod
    def _for_filename_and_lines(cls, filename, lines):
        source_cache = cls._class_local('__source_cache_with_lines', {})
        try:
            return source_cache[(filename, lines)]
        except KeyError:
            pass

        result = source_cache[(filename, lines)] = cls(filename, lines)
        return result

    @classmethod
    def lazycache(cls, frame):
        if hasattr(linecache, 'lazycache'):
            linecache.lazycache(frame.f_code.co_filename, frame.f_globals)

    @classmethod
    def executing(cls, frame_or_tb):
        """
        Returns an `Executing` object representing the operation
        currently executing in the given frame or traceback object.
        """
        if isinstance(frame_or_tb, types.TracebackType):
            # https://docs.python.org/3/reference/datamodel.html#traceback-objects
            # "tb_lineno gives the line number where the exception occurred;
            #  tb_lasti indicates the precise instruction.
            #  The line number and last instruction in the traceback may differ
            #  from the line number of its frame object
            #  if the exception occurred in a try statement with no matching except clause
            #  or with a finally clause."
            tb = frame_or_tb
            frame = tb.tb_frame
            lineno = tb.tb_lineno
            lasti = tb.tb_lasti
        else:
            frame = frame_or_tb
            lineno = frame.f_lineno
            lasti = frame.f_lasti

        code = frame.f_code
        key = (code, id(code), lasti)
        executing_cache = cls._class_local('__executing_cache', {})

        try:
            args = executing_cache[key]
        except KeyError:
            def find(source, retry_cache):
                node = stmts = None
                tree = source.tree
                if tree:
                    try:
                        stmts = source.statements_at_line(lineno)
                        if stmts:
                            if code.co_filename.startswith('<ipython-input-') and code.co_name == '<module>':
                                tree = _extract_ipython_statement(stmts, tree)
                            node = NodeFinder(frame, stmts, tree, lasti).result
                    except Exception as e:
                        # These exceptions can be caused by the source code having changed
                        # so the cached Source doesn't match the running code
                        # (e.g. when using IPython %autoreload)
                        # Try again with a fresh Source object
                        if retry_cache and isinstance(e, (NotOneValueFound, AssertionError)):
                            return find(
                                source=cls.for_frame(frame, use_cache=False),
                                retry_cache=False,
                            )
                        if TESTING:
                            raise

                    if node:
                        new_stmts = {statement_containing_node(node)}
                        assert_(new_stmts <= stmts)
                        stmts = new_stmts

                return source, node, stmts

            args = find(source=cls.for_frame(frame), retry_cache=True)
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
            encoding = Source.detect_encoding(source)
            source = source.decode(encoding)
        return source

    @staticmethod
    def detect_encoding(source):
        return detect_encoding(io.BytesIO(source).readline)[0]

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
        assert_(code.co_filename == self.filename)
        return self._qualnames.get((code.co_name, code.co_firstlineno), code.co_name)


class Executing(object):
    """
    Information about the operation a frame is currently executing.

    Generally you will just want `node`, which is the AST node being executed,
    or None if it's unknown.
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

    def add_qualname(self, node, name=None):
        name = name or node.name
        self.stack.append(name)
        if getattr(node, 'decorator_list', ()):
            lineno = node.decorator_list[0].lineno
        else:
            lineno = node.lineno
        self.qualnames.setdefault((name, lineno), ".".join(self.stack))

    def visit_FunctionDef(self, node, name=None):
        self.add_qualname(node, name)
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

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Lambda(self, node):
        # noinspection PyTypeChecker
        self.visit_FunctionDef(node, '<lambda>')

    def visit_ClassDef(self, node):
        self.add_qualname(node)
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


sentinel = 'io8urthglkjdghvljusketgIYRFYUVGHFRTBGVHKGF78678957647698'


class NodeFinder(object):
    def __init__(self, frame, stmts, tree, lasti):
        self.frame = frame
        self.tree = tree
        self.code = code = frame.f_code
        self.is_pytest = any(
            'pytest' in name.lower()
            for group in [code.co_names, code.co_varnames]
            for name in group
        )

        if self.is_pytest:
            self.ignore_linenos = frozenset(assert_linenos(tree))
        else:
            self.ignore_linenos = frozenset()

        instruction = self.get_actual_current_instruction(lasti)
        op_name = instruction.opname
        self.lasti = instruction.offset

        if op_name.startswith('CALL_'):
            typ = ast.Call
        elif op_name.startswith(('BINARY_SUBSCR', 'SLICE+')):
            typ = ast.Subscript
        elif op_name.startswith('BINARY_'):
            typ = ast.BinOp
        elif op_name.startswith('UNARY_'):
            typ = ast.UnaryOp
        elif op_name in ('LOAD_ATTR', 'LOAD_METHOD', 'LOOKUP_METHOD'):
            typ = ast.Attribute
        elif op_name in ('COMPARE_OP', 'IS_OP', 'CONTAINS_OP'):
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

    def clean_instructions(self, code):
        return [
            inst
            for inst in get_instructions(code)
            if inst.opname != 'EXTENDED_ARG'
            if inst.lineno not in self.ignore_linenos
        ]

    def get_original_clean_instructions(self):
        result = self.clean_instructions(self.code)

        # pypy sometimes (when is not clear)
        # inserts JUMP_IF_NOT_DEBUG instructions in bytecode
        # If they're not present in our compiled instructions,
        # ignore them in the original bytecode
        if not any(
                inst.opname == "JUMP_IF_NOT_DEBUG"
                for inst in self.compile_instructions()
        ):
            result = [
                inst for inst in result
                if inst.opname != "JUMP_IF_NOT_DEBUG"
            ]

        return result

    def matching_nodes(self, exprs):
        original_instructions = self.get_original_clean_instructions()
        original_index = only(
            i
            for i, inst in enumerate(original_instructions)
            if inst.offset == self.lasti
        )
        for i, expr in enumerate(exprs):
            setter = get_setter(expr)
            # noinspection PyArgumentList
            replacement = ast.BinOp(
                left=expr,
                op=ast.Pow(),
                right=ast.Str(s=sentinel),
            )
            ast.fix_missing_locations(replacement)
            setter(replacement)
            try:
                instructions = self.compile_instructions()
            finally:
                setter(expr)
            indices = [
                i
                for i, instruction in enumerate(instructions)
                if instruction.argval == sentinel
            ]

            # There can be several indices when the bytecode is duplicated,
            # as happens in a finally block in 3.9+
            # First we remove the opcodes caused by our modifications
            for index_num, sentinel_index in enumerate(indices):
                # Adjustment for removing sentinel instructions below
                # in past iterations
                sentinel_index -= index_num * 2

                assert_(instructions.pop(sentinel_index).opname == 'LOAD_CONST')
                assert_(instructions.pop(sentinel_index).opname == 'BINARY_POWER')

            # Then we see if any of the instruction indices match
            for index_num, sentinel_index in enumerate(indices):
                sentinel_index -= index_num * 2
                new_index = sentinel_index - 1

                if new_index != original_index:
                    continue

                original_inst = original_instructions[original_index]
                new_inst = instructions[new_index]

                # In Python 3.9+, changing 'not x in y' to 'not sentinel_transformation(x in y)'
                # changes a CONTAINS_OP(invert=1) to CONTAINS_OP(invert=0),<sentinel stuff>,UNARY_NOT
                if (
                        original_inst.opname == new_inst.opname in ('CONTAINS_OP', 'IS_OP')
                        and original_inst.arg != new_inst.arg
                        and (
                        original_instructions[original_index + 1].opname
                        != instructions[new_index + 1].opname == 'UNARY_NOT'
                )):
                    # Remove the difference for the upcoming assert
                    instructions.pop(new_index + 1)

                # Check that the modified instructions don't have anything unexpected
                for inst1, inst2 in zip_longest(original_instructions, instructions):
                    assert_(
                        inst1.opname == inst2.opname or
                        all(
                            'JUMP_IF_' in inst.opname
                            for inst in [inst1, inst2]
                        ) or
                        all(
                            inst.opname in ('JUMP_FORWARD', 'JUMP_ABSOLUTE')
                            for inst in [inst1, inst2]
                        )
                        or (
                                inst1.opname == 'PRINT_EXPR' and
                                inst2.opname == 'POP_TOP'
                        )
                        or (
                                inst1.opname in ('LOAD_METHOD', 'LOOKUP_METHOD') and
                                inst2.opname == 'LOAD_ATTR'
                        )
                        or (
                                inst1.opname == 'CALL_METHOD' and
                                inst2.opname == 'CALL_FUNCTION'
                        ),
                        (inst1, inst2, ast.dump(expr), expr.lineno, self.code.co_filename)
                    )

                yield expr

    def compile_instructions(self):
        module_code = compile_similar_to(self.tree, self.code)
        code = only(self.find_codes(module_code))
        return self.clean_instructions(code)

    def find_codes(self, root_code):
        checks = [
            attrgetter('co_firstlineno'),
            attrgetter('co_name'),
            attrgetter('co_freevars'),
            attrgetter('co_cellvars'),
        ]
        if not self.is_pytest:
            checks += [
                attrgetter('co_names'),
                attrgetter('co_varnames'),
            ]

        def matches(c):
            return all(
                f(c) == f(self.code)
                for f in checks
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

    def get_actual_current_instruction(self, lasti):
        """
        Get the instruction corresponding to the current
        frame offset, skipping EXTENDED_ARG instructions
        """
        # Don't use get_original_clean_instructions
        # because we need the actual instructions including
        # EXTENDED_ARG
        instructions = list(get_instructions(self.code))
        index = only(
            i
            for i, inst in enumerate(instructions)
            if inst.offset == lasti
        )

        while True:
            instruction = instructions[index]
            if instruction.opname != "EXTENDED_ARG":
                return instruction
            index += 1


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


@cache
def statement_containing_node(node):
    while not isinstance(node, ast.stmt):
        node = node.parent
    return node


def assert_linenos(tree):
    for node in ast.walk(tree):
        if (
                hasattr(node, 'parent') and
                hasattr(node, 'lineno') and
                isinstance(statement_containing_node(node), ast.Assert)
        ):
            yield node.lineno


def _extract_ipython_statement(stmts, tree):
    # IPython separates each statement in a cell to be executed separately
    # So NodeFinder should only compile one statement at a time or it
    # will find a code mismatch.
    stmt = list(stmts)[0]
    while not isinstance(stmt.parent, ast.Module):
        stmt = stmt.parent
    # use `ast.parse` instead of `ast.Module` for better portability
    # python3.8 changes the signature of `ast.Module`
    # Inspired by https://github.com/pallets/werkzeug/pull/1552/files
    tree = ast.parse("")
    tree.body = [stmt]
    ast.copy_location(tree, stmt)
    return tree
