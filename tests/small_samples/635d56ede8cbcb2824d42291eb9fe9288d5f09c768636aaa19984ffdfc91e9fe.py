# This sample was generated for the following code mutation detected by mutmut:
# 
# --- tests/deadcode.py
# +++ tests/deadcode.py
# @@ -271,7 +271,7 @@
#              self.walk_deadcode(node.iter, deadcode)
#              self.check_stmts(node.body, deadcode)
#  
# -            else_is_dead = self.check_stmts(node.orelse, deadcode)
# +            else_is_dead = None
#  
#              if else_is_dead and not contains_break(node.body):
#                  # for a in l:
# 

with self:
    for _ in tester:
        pass
    else:
        tester