# This sample was generated for the following code mutation detected by mutmut:
# 
# --- tests/deadcode.py
# +++ tests/deadcode.py
# @@ -99,7 +99,7 @@
#                      node.__static_value = node.body.__static_value
#  
#                  elif cnd is False:
# -                    node.__static_value = node.orelse.__static_value
# +                    node.__static_value = None
#  
#              elif isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And):
#                  if all(self.static_cnd(n) is True for n in node.values):
# 

if 1 if 0 else a:
    print