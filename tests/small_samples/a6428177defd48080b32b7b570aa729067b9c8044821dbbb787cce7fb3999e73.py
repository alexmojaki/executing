# This sample was generated for the following code mutation detected by mutmut:
# 
# --- tests/deadcode.py
# +++ tests/deadcode.py
# @@ -307,7 +307,7 @@
#              self.check_stmts(node.body, deadcode or cnd is False)
#              else_is_dead = self.check_stmts(node.orelse, deadcode or cnd is True)
#  
# -            if cnd is True and not contains_break(node):
# +            if cnd is False and not contains_break(node):
#                  # while True: ... no break
#                  deadcode = True
#  
# 

while 0:
    pass
x = 0