# This sample was generated for the following code mutation detected by mutmut:
# 
# --- executing/_position_node_finder.py
# +++ executing/_position_node_finder.py
# @@ -496,8 +496,7 @@
#          if (
#              node_match(ast.Name, ctx=ast.Load)
#              or (
# -                node_match(ast.Name, ctx=ast.Store)
# -                and isinstance(node.parent, ast.AugAssign)
# +                node_match(ast.Name, ctx=ast.Store) or isinstance(node.parent, ast.AugAssign)
#              )
#          ) and inst_match(
#              ("LOAD_NAME", "LOAD_FAST", "LOAD_GLOBAL", "LOAD_DEREF"), argval=mangled_name(node)
# 

result += src[start_pos]