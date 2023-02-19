import ast


def pos_range(node):
    if isinstance(node, ast.Module):
        start = pos_range(node.body[0])[0]
        end = pos_range(node.body[-1])[1]
        return start, end
    start, end = node, node

    if hasattr(node, "decorator_list") and node.decorator_list:
        start = node.decorator_list[0]

    return (start.lineno, start.col_offset), (end.end_lineno, end.end_col_offset)


def childs(node):
    for child in ast.iter_child_nodes(node):
        if not hasattr(child, "lineno"):
            for c in childs(child):
                yield c
        else:
            yield child


class LinenosCache:
    def __init__(self, tree):
        self.tree = tree
        self.cache = {}

    def __getitem__(self, line):
        if line in self.cache:
            return self.cache[line]

        result = []

        def line_items(node):
            start, end = pos_range(node)

            if hasattr(node, "lineno"):
                if (
                    hasattr(node, "end_lineno")
                    and isinstance(node, ast.expr)
                    and node.lineno <= line <= node.end_lineno
                ):
                    result.append(node)
                elif node.lineno == line:
                    if hasattr(node, "lineno"):
                        result.append(node)

            if start[0] <= line <= end[0]:
                for child in childs(node):
                    line_items(child)

        line_items(self.tree)

        self.cache[line] = result

        return result
