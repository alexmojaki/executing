# This sample was generated for the following code mutation detected by mutmut:
# 
# --- tests/deadcode.py
# +++ tests/deadcode.py
# @@ -71,9 +71,7 @@
#  
#              elif isinstance(node, ast.UnaryOp):
#                  try:
# -                    node.__static_value = self.operator_map[type(node.op)](
# -                        node.operand.__static_value
# -                    )
# +                    node.__static_value = None
#                  except Exception:
#                      pass
#  
# 

if not end_lineno:
    start_lineno