# This sample was generated for the following code mutation detected by mutmut:
# 
# --- tests/deadcode.py
# +++ tests/deadcode.py
# @@ -337,7 +337,7 @@
#          elif isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And):
#              dead_op = deadcode
#              for v in node.values:
# -                if self.static_value(v, dead_op) is False:
# +                if self.static_value(v, dead_op) is True:
#                      dead_op = True
#  
#          elif isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
# 

print(0 and foo)