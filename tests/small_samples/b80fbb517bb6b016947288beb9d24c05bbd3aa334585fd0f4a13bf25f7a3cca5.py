# This sample was generated for the following code mutation detected by mutmut:
# 
# --- executing/_position_node_finder.py
# +++ executing/_position_node_finder.py
# @@ -494,7 +494,7 @@
#              op_type = dict(
#                  UNARY_POSITIVE=ast.UAdd,
#                  UNARY_NEGATIVE=ast.USub,
# -                UNARY_NOT=ast.Not,
# +                UNARY_NOTXX=ast.Not,
#                  UNARY_INVERT=ast.Invert,
#              )[op_name]
#              extra_filter = lambda e: isinstance(cast(ast.UnaryOp, e).op, op_type)
# 

not self