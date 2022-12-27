# This sample was generated for the following code mutation detected by mutmut:
# 
# --- tests/deadcode.py
# +++ tests/deadcode.py
# @@ -105,7 +105,7 @@
#                  if all(self.static_cnd(n) is True for n in node.values):
#                      node.__static_value = True
#  
# -                if any(self.static_cnd(n) is False for n in node.values):
# +                if any(self.static_cnd(n) is not False for n in node.values):
#                      node.__static_value = False
#  
#              elif isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
# 

if isinstance and node:
    self