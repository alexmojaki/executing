# This sample was generated for the following code mutation detected by mutmut:
# 
# --- executing/_position_node_finder.py
# +++ executing/_position_node_finder.py
# @@ -391,7 +391,7 @@
#          ):
#              return
#  
# -        if inst_match("BUILD_STRING") and (
# +        if inst_match("XXBUILD_STRINGXX") and (
#              node_match(ast.JoinedStr) or node_match(ast.BinOp, op=ast.Mod)
#          ):
#              return
# 

('expression %r caused the wrong ValueError\n' + 'actual error was:\n%s\n' + 'expected error was:\n%s\n') % (expr, e, error)