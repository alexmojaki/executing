import sys
import pathlib
import dis
import types

from executing import Source
from executing._exceptions import KnownIssue,VerifierFailure,NoMatch
from executing import NotOneValueFound
import executing

executing.executing.TESTING = 1

from rich import print as rprint
import rich

import traceback

import rich.syntax
from rich.console import Console
from rich.table import Table, Column
from rich.highlighter import ReprHighlighter

import ast
from deadcode import is_deadcode

from cProfile import Profile


class Frame:
    pass


class App:
    def inspect_opcode(self, bytecode, index, lineno):
        frame = Frame()
        frame.f_lasti = index
        frame.f_code = bytecode
        frame.f_globals = globals()
        frame.f_lineno = lineno

        self.profile.enable()
        source = Source.for_frame(frame)

        try:
            ex = Source.executing(frame)
            result = "[green]" + type(ex.node).__name__
            if hasattr(ex.node, "name"):
                result += "(" + str(ex.node.name) + ")"
            elif hasattr(ex.node, "id"):
                result += "(" + ex.node.id + ")"
            elif hasattr(ex.node, "attr"):
                result += "(." + ex.node.attr + ")"
            elif hasattr(ex.node, "value"):
                result += f"({ex.node.value})"

            if ex.decorator:
                result += " @%s" % ex.decorator
            return result
        except RuntimeError:
            raise
        except (KnownIssue,VerifierFailure,NoMatch,NotOneValueFound,AssertionError) as e:
            color= "[yellow]" if isinstance(e,KnownIssue) else "[red]"
            return color + type(e).__name__ + ": " + str(e).split("\n")[0]
        finally:
            self.profile.disable()

    def inspect(self, bc):
        first = True
        table = Table(
            title=bc.co_name + ":",
            box=None,
            title_style="blue",
            title_justify="left",
        )

        table.add_column("offset", justify="right")

        if sys.version_info >= (3, 11):
            table.add_column("start")
            table.add_column("end")
        else:
            table.add_column("line")

        table.add_column("instruction")
        table.add_column("ast-node")

        highlighter = ReprHighlighter()

        starts_line = None

        for i in dis.get_instructions(
            bc, **({"show_caches": True} if sys.version_info >= (3, 11) else {})
        ):
            if i.starts_line is not None:
                starts_line = i.starts_line

            if sys.version_info >= (3, 11):
                in_range = (
                    i.positions.lineno is not None
                    and i.positions.lineno <= self.end
                    and self.start <= i.positions.end_lineno
                )
            else:
                in_range = (
                    starts_line is not None and self.start <= starts_line <= self.end
                )

            if in_range:
                if first:
                    first = False

                ex = self.inspect_opcode(bc, i.offset, starts_line)

                if sys.version_info >= (3, 11):
                    positions = (
                        "%s:%s" % (i.positions.lineno, i.positions.col_offset),
                        "%s:%s" % (i.positions.end_lineno, i.positions.end_col_offset),
                    )
                else:
                    positions = (str(starts_line),)

                table.add_row(
                    str(i.offset),
                    *positions,
                    highlighter("%s(%s)" % (i.opname, i.argval)),
                    ex,
                    style="on grey19" if i.opname == "CACHE" else "on grey30"
                    # **({"style":"on white" } if i.opname=="CACHE" else {})
                )

        if first == False:
            self.console.print()
            self.console.print(table)

        for const in bc.co_consts:
            if isinstance(const, types.CodeType):
                self.inspect(const)

    def dump_deadcode(self, filename):
        from rich import print as rprint
        from rich.tree import Tree
        from rich.syntax import Syntax

        print(filename)
        with open(filename) as file:
            code = file.read()
            tree = ast.parse(code)

        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node

        node = tree

        def report(node, tree):

            if isinstance(
                node, (ast.expr_context, ast.operator, ast.unaryop, ast.cmpop)
            ):
                return

            if isinstance(node, (ast.stmt, ast.expr)):
                deadcode = is_deadcode(node)
            else:
                deadcode = None

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

            t = tree.add("%s %s" % (name, deadcode) + (" %s:%s"%(node.lineno,node.end_lineno) if hasattr(node,"lineno") else ""))
            dots = False

            for child in ast.iter_child_nodes(node):
                if (
                    hasattr(child, "lineno")
                    and ( child.lineno > self.end
                    or self.start > child.end_lineno)
                ):
                    if not dots:
                        tree.add("...")
                        dots = True
                    continue

                report(child, t)
                dots = False

        tree = Tree("ast")
        report(node, tree)
        rprint(tree)

    def main(self):
        import sys

        if len(sys.argv) <= 1 or sys.argv[1] in ("--help", "-h"):
            print(
                """
        analyse.py <filename> [line | first_line:last_line]

        Analyses a range in the given source in the specified range
        and maps every bytecode to the node found by executing.
        """
            )
            sys.exit(0)


        self.profile=Profile()

        filename = pathlib.Path(sys.argv[1])

        if ":" in sys.argv[2]:
            self.start, self.end = sys.argv[2].split(":")
            self.start = int(self.start)
            self.end = int(self.end)
        else:
            self.start = self.end = int(sys.argv[2])

        code = filename.read_text()
        self.console = Console()

        self.console.print(
            rich.syntax.Syntax(
                code, "python", line_numbers=True, line_range=(self.start, self.end)
            )
        )

        print("all bytecodes in this range:")

        if 0:
            code=ast.parse(code,filename,"exec")
            for i,node in enumerate(ast.walk(code)):
                node.lineno=i*2
                node.end_lineno=i*2+1

        bc = compile(code, filename, "exec")
        self.inspect(bc)

        self.dump_deadcode(filename)


        #self.profile.print_stats(sort="cumtime")


if __name__ == "__main__":
    App().main()
