# This sample was generated for the following code mutation detected by mutmut:
# 
# --- tests/deadcode.py
# +++ tests/deadcode.py
# @@ -241,7 +241,7 @@
#  
#              if_is_dead = self.check_stmts(node.body, deadcode or (test_value is False))
#              else_is_dead = self.check_stmts(
# -                node.orelse, deadcode or (test_value is True)
# +                node.orelse, deadcode or (test_value is False)
#              )
#  
#              self.walk_deadcode(node.test, deadcode)
# 

if False:
    pass
self