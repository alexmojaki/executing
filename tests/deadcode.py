import ast
import operator


def contains_break(node_or_list):
    "search all child nodes except other loops for a break statement"

    if isinstance(node_or_list, ast.AST):
        childs = ast.iter_child_nodes(node_or_list)
    elif isinstance(node_or_list, list):
        childs = node_or_list
    else:
        raise TypeError(node_or_list)

    for child in childs:
        if isinstance(child, (ast.For, ast.While, ast.AsyncFor)):
            if contains_break(child.orelse):
                return True
        elif isinstance(child, ast.Break):
            return True
        elif contains_break(child):
            return True

    return False



class Deadcode:
    @staticmethod
    def annotate(tree):
        deadcode = Deadcode()

        deadcode.annotate_static_values(tree)
        deadcode.walk_deadcode(tree, False)

    def __init__(self):
        self.future_annotations = False

    operator_map = {
        # binary
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.LShift: operator.lshift,
        ast.RShift: operator.rshift,
        ast.BitOr: operator.or_,
        ast.BitXor: operator.xor,
        ast.BitAnd: operator.and_,
        ast.MatMult: operator.matmul,
        # unary
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
        ast.Not: operator.not_,
        ast.Invert: operator.invert,
    }

    def annotate_static_values(self, node):
        for n in ast.iter_child_nodes(node):
            self.annotate_static_values(n)

        try:
            if isinstance(node, ast.Constant):
                node.__static_value = node.value

            elif isinstance(node, ast.Name) and node.id == "__debug__":
                node.__static_value = True

            elif isinstance(node, ast.UnaryOp):
                try:
                    node.__static_value = self.operator_map[type(node.op)](
                        node.operand.__static_value
                    )
                except Exception:
                    pass

            elif isinstance(node, ast.BinOp):
                try:
                    node.__static_value = self.operator_map[type(node.op)](
                        node.left.__static_value, node.right.__static_value
                    )

                    if (
                        isinstance(node.__static_value, (str, bytes))
                        and len(node.__static_value) > 4000
                    ):
                        # do not perform big string operations
                        # TODO: check if this constraint is correct
                        del node.__static_value
                except Exception:
                    pass

            elif isinstance(node, ast.Subscript):
                try:
                    node.__static_value = node.value.__static_value[
                        node.slice.__static_value
                    ]
                except Exception:
                    pass

            elif isinstance(node, ast.IfExp):
                cnd = self.static_cnd(node.test)
                if cnd is True:
                    node.__static_value = node.body.__static_value

                elif cnd is False:
                    node.__static_value = node.orelse.__static_value

            elif isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And):
                if all(self.static_cnd(n) is True for n in node.values):
                    node.__static_value = True

                if any(self.static_cnd(n) is False for n in node.values):
                    node.__static_value = False

            elif isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
                if all(self.static_cnd(n) is False for n in node.values):
                    node.__static_value = False

                if any(self.static_cnd(n) is True for n in node.values):
                    node.__static_value = True

        except AttributeError as e:
            if e.name != "_Deadcode__static_value":
                raise

    def static_cnd(self, node):
        try:
            return bool(node.__static_value)
        except AttributeError:
            return None

    def has_static_value(self,node):
        try:
            node.__static_value
        except AttributeError:
            return False
        return True


    def static_value(self, node, deadcode):
        self.walk_deadcode(node, deadcode)
        return self.static_cnd(node)

    def check_stmts(self, stmts, deadcode):
        """
        used to check the body: of a function, if, ...
        """
        for stmt in stmts:
            stmt.deadcode = deadcode

            if self.walk_deadcode(stmt, deadcode):
                deadcode = True
        return deadcode

    def check_childs(self, childs, deadcode):
        """
        used to check childs: function arguments
        """
        for child in childs:
            self.walk_deadcode(child, deadcode)

    def walk_annotation(self, annotation, deadcode):
        if self.future_annotations:
            deadcode = True
        self.walk_deadcode(annotation, deadcode)

    def walk_deadcode(self, node, deadcode):
        "returns True if this statement will never return"

        # this check is not perfect but better than nothing
        # it tries to prevent a lot of "node without associated Bytecode" errors

        # They were generated test driven.
        # Every case represented here is derived from a error where python performed dead code elimination.

        if node is None:
            return

        if isinstance(node, list):
            for child in node:
                self.walk_deadcode(child, deadcode)
            return

        node.deadcode = deadcode or getattr(node, "deadcode", False)

        if isinstance(node, ast.Module):
            for stmt in node.body:
                if isinstance(stmt, ast.ImportFrom):
                    if stmt.module == "__future__" and any(
                        "annotations" == alias.name for alias in stmt.names
                    ):
                        self.future_annotations = True

            self.check_stmts(node.body, deadcode)
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            self.check_childs(node.items, deadcode)
            self.check_stmts(node.body, deadcode)

        elif isinstance(node, (ast.Return, ast.Break, ast.Continue, ast.Raise)):
            if isinstance(node, ast.Raise):
                self.walk_deadcode(node.exc, deadcode)
                self.walk_deadcode(node.cause, deadcode)

            if isinstance(node, ast.Return):
                self.walk_deadcode(node.value, deadcode)

            deadcode = True

        elif isinstance(node, ast.Assert):
            cnd = self.static_value(node.test, deadcode)

            if cnd is False:
                node.deadcode = deadcode
                self.walk_deadcode(node.msg, deadcode)
                deadcode = True

            elif cnd is True:
                node.deadcode = deadcode
                self.walk_deadcode(node.msg, True)

            else:
                node.deadcode = deadcode
                self.walk_deadcode(node.msg, deadcode)

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            self.walk_annotation(node.args.posonlyargs, deadcode)
            self.walk_annotation(node.args.args, deadcode)
            self.walk_annotation(node.args.kwonlyargs, deadcode)

            self.walk_annotation(node.args.vararg, deadcode)
            self.walk_annotation(node.args.kwarg, deadcode)

            self.check_childs(node.args.kw_defaults, deadcode)
            self.check_childs(node.args.defaults, deadcode)

            self.walk_annotation(node.returns, deadcode)
            self.check_childs(node.decorator_list, deadcode)

            self.check_stmts(node.body, deadcode)

        elif isinstance(node, ast.ClassDef):
            self.check_childs(node.decorator_list, deadcode)

            self.check_childs(node.bases, deadcode)

            self.check_childs(node.keywords, deadcode)

            self.check_stmts(node.body, deadcode)

        elif isinstance(node, ast.If):

            test_value = self.static_value(node.test, deadcode)

            if_is_dead = self.check_stmts(node.body, deadcode or (test_value is False))
            else_is_dead = self.check_stmts(
                node.orelse, deadcode or (test_value is True)
            )

            self.walk_deadcode(node.test, deadcode)

            deadcode = if_is_dead and else_is_dead

        elif isinstance(node, ast.Match):
            self.walk_deadcode(node.subject, deadcode)
            for case_ in node.cases:
                case_.deadcode = deadcode
                self.walk_deadcode(case_.pattern, deadcode)
                self.walk_deadcode(case_.guard, deadcode)

            dead_cases = all(
                [self.check_stmts(case_.body, deadcode or self.static_cnd(case_.guard) is False ) for case_ in node.cases]
            )

            if any(
                isinstance(case_.pattern, ast.MatchAs) and case_.pattern.pattern is None
                for case_ in node.cases
            ):
                # case _:
                deadcode = dead_cases

        elif isinstance(node, (ast.For, ast.AsyncFor)):
            self.walk_deadcode(node.target, deadcode)
            self.walk_deadcode(node.iter, deadcode)
            self.check_stmts(node.body, deadcode)

            else_is_dead = self.check_stmts(node.orelse, deadcode)

            if else_is_dead and not contains_break(node.body):
                # for a in l:
                #     something()
                # else:
                #     return None
                # deadcode()
                deadcode = True

        elif isinstance(node, ast.IfExp):

            test_value = self.static_value(node.test, deadcode)

            self.walk_deadcode(
                node.body, deadcode or (test_value is False)
            )

            self.walk_deadcode(
                node.orelse, deadcode or (test_value is True)
            )

        elif isinstance(node, (ast.While)):
            cnd = self.static_value(node.test, deadcode)

            self.check_stmts(node.body, deadcode or cnd is False)
            else_is_dead = self.check_stmts(node.orelse, deadcode or cnd is True)

            if cnd is True and not contains_break(node):
                # while True: ... no break
                deadcode = True

            if else_is_dead and not contains_break(node.body):
                # for a in l:
                #     something()
                # else:
                #     return None
                # deadcode()
                deadcode = True

        elif isinstance(node, (ast.Try, ast.TryStar)):
            try_dead = self.check_stmts(node.body, deadcode)

            for handler in node.handlers:
                handler.deadcode = deadcode
                self.walk_deadcode(handler.type, deadcode)

            handlers_dead = all(
                [self.check_stmts(h.body, deadcode) for h in node.handlers]
            )
            else_dead = self.check_stmts(node.orelse, try_dead)
            final_dead = self.check_stmts(node.finalbody, deadcode)

            deadcode = (handlers_dead and else_dead) or final_dead

        elif isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And):
            dead_op = deadcode
            for v in node.values:
                if self.static_value(v, dead_op) is False:
                    dead_op = True

        elif isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
            dead_op = deadcode
            for v in node.values:
                if self.static_value(v, dead_op) is True:
                    dead_op = True

        elif isinstance(node, ast.Expr):
            # dead expressions:
            # > 5+5
            # for example
            dead_expr = self.has_static_value(node.value)
            if (
                isinstance(
                    node.parent,
                    (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef),
                )
                and node.parent.body[0] == node
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
            ):
                # docstring
                dead_expr = False

            self.walk_deadcode(node.value, dead_expr or deadcode)

        else:

            for n in ast.iter_child_nodes(node):
                self.walk_deadcode(n, deadcode)

        return deadcode


def dump_deadcode(node):
    from rich import print as rprint
    from rich.tree import Tree

    def report(node, tree):
        if isinstance(node, (ast.expr_context, ast.operator, ast.unaryop, ast.cmpop)):
            return

        deadcode = getattr(node, "deadcode", None)
        if deadcode is None:
            deadcode = "[red]<undefined>"
        else:
            deadcode = "[red]dead" if deadcode else "[blue]used"

        name = type(node).__name__

        if isinstance(node, ast.Name):
            name += "(%s)" % node.id

        if isinstance(node, ast.Attribute):
            name += "(.%s)" % node.attr

        if hasattr(node, "_Deadcode__static_value"):
            name += " == %r" % getattr(node, "_Deadcode__static_value")

        t = tree.add("%s %s" % (name, deadcode))
        for child in ast.iter_child_nodes(node):
            report(child, t)

    tree = Tree("ast")
    report(node, tree)
    rprint(tree)


def main():
    import sys

    filename = sys.argv[1]
    print(filename)
    with open(filename) as file:
        tree = ast.parse(file.read())

    Deadcode.annotate(tree)

    dump_deadcode(tree)


if __name__ == "__main__":
    main()
