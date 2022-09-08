import ast


class Deadcode:
    @staticmethod
    def annotate(tree):
        Deadcode().walk_deadcode(tree, False)

    def __init__(self):
        self.future_annotations = False

    def static_value(self, node, deadcode):

        node.deadcode = deadcode or getattr(node, "deadcode", False)

        if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And):
            result = None
            for v in node.values:
                if self.static_value(v, deadcode) == False:
                    result = False
                    deadcode = True
            return result

        elif isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
            result = None
            for v in node.values:
                if self.static_value(v, deadcode) == True:
                    result = True
                    deadcode = True
            return result

        elif isinstance(node, ast.Constant):
            return bool(node.value)
        elif isinstance(node, ast.Name) and node.id == "__debug__":
            return True

        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            v = self.static_value(node.operand, deadcode)
            if isinstance(v, bool):
                return not v
        else:
            for n in ast.iter_child_nodes(node):
                self.walk_deadcode(n, deadcode)

        return None

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
            deadcode = self.check_stmts(node.body, deadcode)

        elif isinstance(node, (ast.Return, ast.Break, ast.Continue, ast.Raise)):
            if isinstance(node, ast.Raise):
                self.walk_deadcode(node.exc, deadcode)
                self.walk_deadcode(node.cause, deadcode)

            if isinstance(node, ast.Return):
                self.walk_deadcode(node.value, deadcode)

            deadcode = True

        elif isinstance(node, ast.Assert):
            cnd = self.static_value(node.test, deadcode)

            if cnd == False:
                deadcode = True
                self.walk_deadcode(node.msg, deadcode)

            elif cnd == True:
                node.deadcode = True
                self.walk_deadcode(node.msg, True)
                self.walk_deadcode(node.test, True)

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

            if_is_dead = self.check_stmts(node.body, deadcode or (test_value == False))
            else_is_dead = self.check_stmts(
                node.orelse, deadcode or (test_value == True)
            )
            deadcode = if_is_dead and else_is_dead

            self.walk_deadcode(node.test, (if_is_dead and not node.orelse) or deadcode)

        elif isinstance(node, ast.Match):
            self.walk_deadcode(node.subject, deadcode)
            for _case in node.cases:
                _case.deadcode = deadcode
                self.walk_deadcode(_case.pattern, deadcode)
                self.walk_deadcode(_case.guard, deadcode)

            dead_cases = all(
                [self.check_stmts(_case.body, deadcode) for _case in node.cases]
            )

            if any(
                isinstance(_case.pattern, ast.MatchAs) and _case.pattern.pattern is None
                for _case in node.cases
            ):
                # case _:
                deadcode = dead_cases

        elif isinstance(node, (ast.For, ast.AsyncFor)):
            self.walk_deadcode(node.target, deadcode)
            self.walk_deadcode(node.iter, deadcode)
            self.check_stmts(node.body, deadcode)
            self.check_stmts(node.orelse, deadcode)

        elif isinstance(node, ast.IfExp):

            test_value = self.static_value(node.test, deadcode)

            if_is_dead = self.walk_deadcode(
                node.body, deadcode or (test_value == False)
            )
            else_is_dead = self.walk_deadcode(
                node.orelse, deadcode or (test_value == True)
            )

        elif isinstance(node, (ast.While)):
            cnd = self.static_value(node.test, deadcode)

            self.check_stmts(node.body, deadcode or cnd == False)
            self.check_stmts(node.orelse, deadcode or cnd == False or cnd == True)

            def contains_break(node):
                "search all child nodes except other loops for a break statement"
                for child in ast.iter_child_nodes(node):
                    if isinstance(child, (ast.For, ast.While, ast.AsyncFor)):
                        continue
                    if isinstance(child, ast.Break):
                        return True
                    if contains_break(child):
                        return True

                return False

            if self.static_value(node.test, deadcode) == True and not contains_break(
                node
            ):
                # while True: ... no break
                deadcode = True

        elif isinstance(node, (ast.Try, ast.TryStar)):
            try_dead = self.check_stmts(node.body, deadcode)

            for handler in node.handlers:
                self.walk_deadcode(handler.type, deadcode)

            handlers_dead = all(
                [self.check_stmts(h.body, deadcode) for h in node.handlers]
            )
            else_dead = self.check_stmts(node.orelse, try_dead)
            final_dead = self.check_stmts(node.finalbody, deadcode)

            deadcode = (handlers_dead and else_dead) or final_dead

        else:

            self.static_value(node, deadcode)

        return deadcode


if __name__ == "__main__":
    import sys
    from rich import print as rprint
    from rich.tree import Tree

    filename = sys.argv[1]
    print(filename)
    with open(filename) as file:
        tree = ast.parse(file.read())

    Deadcode.annotate(tree)

    def report(node, tree):
        if isinstance(node, (ast.expr_context, ast.operator, ast.unaryop, ast.cmpop)):
            return

        deadcode = getattr(node, "deadcode", None)
        if deadcode is None:
            deadcode = "[red]<undefined>"
        else:
            deadcode = "[red]dead" if deadcode else "[blue]used"

        t = tree.add("%s %s" % (type(node).__name__, deadcode))
        for child in ast.iter_child_nodes(node):
            report(child, t)

    rtree = Tree("ast")
    report(tree, rtree)
    rprint(rtree)