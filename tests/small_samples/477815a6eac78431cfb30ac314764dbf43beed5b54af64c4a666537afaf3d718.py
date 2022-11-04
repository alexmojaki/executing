# This sample was generated for the following code mutation detected by mutmut:
# 
# --- tests/deadcode.py
# +++ tests/deadcode.py
# @@ -67,7 +67,7 @@
#                  node.__static_value = node.value
#  
#              elif isinstance(node, ast.Name) and node.id == "__debug__":
# -                node.__static_value = True
# +                node.__static_value = False
#  
#              elif isinstance(node, ast.UnaryOp):
#                  try:
# 

if __debug__:
    self