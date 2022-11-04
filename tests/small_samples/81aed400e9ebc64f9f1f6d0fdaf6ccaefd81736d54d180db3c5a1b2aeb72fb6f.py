# This sample was generated for the following code mutation detected by mutmut:
# 
# --- tests/deadcode.py
# +++ tests/deadcode.py
# @@ -329,7 +329,7 @@
#              handlers_dead = all(
#                  [self.check_stmts(h.body, deadcode) for h in node.handlers]
#              )
# -            else_dead = self.check_stmts(node.orelse, try_dead)
# +            else_dead = None
#              final_dead = self.check_stmts(node.finalbody, deadcode)
#  
#              deadcode = (handlers_dead and else_dead) or final_dead
# 

try:
    length = len(val)
except:
    pass
else:
    result.set_meta('len', length)