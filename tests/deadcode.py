import ast
import copy
import dis


sentinel_rep = 2
# generate sentinel at runtime to keep it out of the bytecode
# this allows the algorithm to check also this file
sentinel = "xsglegahghegflgfaih" * sentinel_rep


class DeadcodeTransformer(ast.NodeTransformer):
    def visit(self, node):
        if getattr(node, "_check_is_deadcode", False):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                # docstring for example
                return ast.Constant(value=sentinel)

            elif isinstance(node, ast.stmt):
                return ast.Expr(
                    value=ast.Call(
                        func=ast.Name(id="foo", ctx=ast.Load()),
                        args=[ast.Constant(value=sentinel)],
                        keywords=[],
                    )
                )
            elif isinstance(node, ast.expr):
                if hasattr(node, "ctx") and isinstance(node.ctx, (ast.Store, ast.Del)):
                    return ast.Subscript(
                        value=ast.Name(id="foo", ctx=ast.Load()),
                        slice=ast.Constant(value=sentinel),
                        ctx=node.ctx,
                    )

                else:

                    return ast.Subscript(
                        value=ast.Tuple(
                            elts=[node, ast.Constant(value=sentinel)],
                            ctx=ast.Load(),
                        ),
                        slice=ast.Constant(value=0),
                        ctx=ast.Load(),
                    )
            else:
                raise TypeError(node)

        else:
            return super().visit(node)


def is_deadcode(node):

    if isinstance(node, ast.withitem):
        node = node.context_expr

    if isinstance(node, ast.ExceptHandler):
        node = node.body[0]

    if isinstance(node.parent, ast.AnnAssign) and node.parent.target is node:
        # AnnAssign.target has to be ast.Name
        node = node.parent

    if hasattr(node, "_is_deadcode"):
        return node._is_deadcode

    node._check_is_deadcode = True

    module = node
    while hasattr(module, "parent"):
        module = module.parent

    assert isinstance(module, ast.Module)

    # create working copy of the ast
    module2 = copy.deepcopy(module)
    del node._check_is_deadcode

    module2 = ast.fix_missing_locations(DeadcodeTransformer().visit(module2))

    try:
        code = compile(module2, "<filename>", "exec")
    except:
        print(ast.dump(module2, indent=2))
        raise

    visited = set()

    def contains_sentinel(code):
        if code in visited:
            return False

        for inst in dis.get_instructions(code):
            arg = inst.argval
            if isinstance(arg, type(code)) and contains_sentinel(arg):
                return True
            if arg == sentinel:
                return True

        visited.add(code)
        return False

    node._is_deadcode = not contains_sentinel(code)

    return node._is_deadcode
