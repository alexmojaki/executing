# This sample was generated for the following code mutation detected by mutmut:
# 
# --- tests/deadcode.py
# +++ tests/deadcode.py
# @@ -109,7 +109,7 @@
#                      node.__static_value = False
#  
#              elif isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
# -                if all(self.static_cnd(n) is False for n in node.values):
# +                if all(self.static_cnd(n) is not False for n in node.values):
#                      node.__static_value = False
#  
#                  if any(self.static_cnd(n) is True for n in node.values):
# 

if level or (level):
    sample_type = 'big'
else:
    pass