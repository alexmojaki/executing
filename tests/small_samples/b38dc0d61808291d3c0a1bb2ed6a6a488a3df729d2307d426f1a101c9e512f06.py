# This sample was generated for the following code mutation detected by mutmut:
# 
# --- tests/deadcode.py
# +++ tests/deadcode.py
# @@ -106,7 +106,7 @@
#                      node.__static_value = True
#  
#                  if any(self.static_cnd(n) is False for n in node.values):
# -                    node.__static_value = False
# +                    node.__static_value = True
#  
#              elif isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
#                  if all(self.static_cnd(n) is False for n in node.values):
# 

if outer and False:
    self