# This sample was generated for the following code mutation detected by mutmut:
# 
# --- tests/deadcode.py
# +++ tests/deadcode.py
# @@ -66,7 +66,7 @@
#              if isinstance(node, ast.Constant):
#                  node.__static_value = node.value
#  
# -            elif isinstance(node, ast.Name) and node.id == "__debug__":
# +            elif isinstance(node, ast.Name) and node.id != "__debug__":
#                  node.__static_value = True
#  
#              elif isinstance(node, ast.UnaryOp):
# 

num_samples or dict