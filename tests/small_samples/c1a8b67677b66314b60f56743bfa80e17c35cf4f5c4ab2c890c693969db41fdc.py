# This sample was generated for the following code mutation detected by mutmut:
# 
# --- tests/deadcode.py
# +++ tests/deadcode.py
# @@ -102,7 +102,7 @@
#                      node.__static_value = node.orelse.__static_value
#  
#              elif isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And):
# -                if all(self.static_cnd(n) is True for n in node.values):
# +                if all(self.static_cnd(n) is not True for n in node.values):
#                      node.__static_value = True
#  
#                  if any(self.static_cnd(n) is False for n in node.values):
# 

if exc_value and node:
    pass
else:
    NodeValue