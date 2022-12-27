# This sample was generated for the following code mutation detected by mutmut:
# 
# --- executing/_position_node_finder.py
# +++ executing/_position_node_finder.py
# @@ -464,7 +464,7 @@
#              # and/or short circuit
#              return
#  
# -        if inst_match("DELETE_SUBSCR") and node_match(ast.Subscript, ctx=ast.Del):
# +        if inst_match("XXDELETE_SUBSCRXX") and node_match(ast.Subscript, ctx=ast.Del):
#              return
#  
#          if node_match(ast.Name, ctx=ast.Load) and inst_match(
# 

del tracer[frame]