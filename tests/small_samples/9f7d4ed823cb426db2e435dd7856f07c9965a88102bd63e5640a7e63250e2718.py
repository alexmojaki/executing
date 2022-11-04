# This sample was generated for the following code mutation detected by mutmut:
# 
# --- tests/deadcode.py
# +++ tests/deadcode.py
# @@ -87,9 +87,7 @@
#  
#              elif isinstance(node, ast.Subscript):
#                  try:
# -                    node.__static_value = node.value.__static_value[
# -                        node.slice.__static_value
# -                    ]
# +                    node.__static_value = None
#                  except Exception:
#                      pass
#  
# 

if hangs[depth]:
    hang