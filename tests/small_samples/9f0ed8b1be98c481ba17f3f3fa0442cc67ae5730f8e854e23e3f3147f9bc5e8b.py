# This sample was generated for the following code mutation detected by mutmut:
# 
# --- tests/deadcode.py
# +++ tests/deadcode.py
# @@ -240,9 +240,7 @@
#              test_value = self.static_value(node.test, deadcode)
#  
#              if_is_dead = self.check_stmts(node.body, deadcode or (test_value is False))
# -            else_is_dead = self.check_stmts(
# -                node.orelse, deadcode or (test_value is True)
# -            )
# +            else_is_dead = None
#  
#              self.walk_deadcode(node.test, deadcode)
#  
# 

if i:
    pass
else:
    loop