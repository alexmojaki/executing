# This sample was generated for the following code mutation detected by mutmut:
# 
# --- tests/deadcode.py
# +++ tests/deadcode.py
# @@ -197,7 +197,7 @@
#          elif isinstance(node, ast.Assert):
#              cnd = self.static_value(node.test, deadcode)
#  
# -            if cnd is False:
# +            if cnd is not False:
#                  node.deadcode = deadcode
#                  self.walk_deadcode(node.msg, deadcode)
#                  deadcode = True
# 

with self as session:
    assert isinstance
    db_func