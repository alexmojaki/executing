import sys
import pathlib
import dis
import types
import inspect

from executing import Source
import executing

executing.executing.TESTING = 1

from rich import print as rprint
import rich


class Frame:
    pass


if len(sys.argv) <= 1 or sys.argv[1] in ("--help", "-h"):
    print(
        """
analyse.py <filename> [line | first_line:last_line]

Analyses a range in the given source in the specified range
and maps every bytecode to the node found by executing.
"""
    )
    sys.exit(0)

filename = pathlib.Path(sys.argv[1])

if ":" in sys.argv[2]:
    start, end = sys.argv[2].split(":")
    start = int(start)
    end = int(end)
else:
    start = end = int(sys.argv[2])


code = filename.read_text()


def inspect_opcode(bytecode, index, lineno):
    frame = Frame()
    frame.f_lasti = index
    frame.f_code = bytecode
    frame.f_globals = globals()
    frame.f_lineno = lineno
    source = Source.for_frame(frame)

    try:
        ex = Source.executing(frame)
    except RuntimeError:
        raise
    except Exception as e:
        return "[red]" + type(e).__name__ + ": " + str(e).split("\n")[0]

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
        


import rich.syntax
from rich.console import Console
from rich.table import Table, Column
from rich.highlighter import ReprHighlighter

console = Console()

console.print(
    rich.syntax.Syntax(code, "python", line_numbers=True, line_range=(start, end))
)


print("all bytecodes in this range:")

bc = compile(code, filename, "exec")


def inspect(bc):
    first = True
    table = Table(
        title=bc.co_name + ":",
        box=None,
        title_style="blue",
        title_justify="left",
    )
    
    table.add_column("offset", justify="right")
    table.add_column("start")
    table.add_column("end")
    table.add_column("instruction")
    table.add_column("ast-node")


    highlighter=ReprHighlighter()

    for i in dis.get_instructions(bc, show_caches=True):

        if (
            i.positions.lineno is not None
            and i.positions.lineno <= end
            and start <= i.positions.end_lineno
        ):
            if first:
                first = False


            ex = inspect_opcode(bc, i.offset, i.positions.lineno)

            table.add_row(
                str(i.offset),
                "%s:%s" % (i.positions.lineno, i.positions.col_offset),
                "%s:%s" % (i.positions.end_lineno, i.positions.end_col_offset),
                highlighter("%s(%s)" % (i.opname, i.argval)),
                ex,
                style="on grey19" if i.opname=="CACHE" else "on grey30"
                #**({"style":"on white" } if i.opname=="CACHE" else {})
            )

    if first == False:
        console.print()
        console.print(table)

    for const in bc.co_consts:
        if isinstance(const, types.CodeType):
            inspect(const)


inspect(bc)
