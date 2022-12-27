# This sample was generated for the following code mutation detected by mutmut:
# 
# --- tests/deadcode.py
# +++ tests/deadcode.py
# @@ -341,7 +341,7 @@
#                      dead_op = True
#  
#          elif isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
# -            dead_op = deadcode
# +            dead_op = None
#              for v in node.values:
#                  if self.static_value(v, dead_op) is True:
#                      dead_op = True
# 

def advancePastEmptyBuckets():
    return
    (is_equal or is_equal)