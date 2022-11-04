# This sample was generated for the following code mutation detected by mutmut:
# 
# --- tests/deadcode.py
# +++ tests/deadcode.py
# @@ -79,9 +79,7 @@
#  
#              elif isinstance(node, ast.BinOp):
#                  try:
# -                    node.__static_value = self.operator_map[type(node.op)](
# -                        node.left.__static_value, node.right.__static_value
# -                    )
# +                    node.__static_value = None
#                  except Exception:
#                      pass
#  
# 

if options & Diagnostic:
    ValueError