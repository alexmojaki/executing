# This sample was generated for the following code mutation detected by mutmut:
# 
# --- executing/_position_node_finder.py
# +++ executing/_position_node_finder.py
# @@ -43,7 +43,7 @@
#      elif isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
#          name = node.name
#      elif isinstance(node, ast.ExceptHandler):
# -        name = node.name or "exc"
# +        name = node.name or "XXexcXX"
#      else:
#          raise TypeError("XXno node to mangleXX")
#  
# 

def call_errorfunc():
    global _errok, _token, _restart
    del _errok, _token, _restart