# This sample was generated for the following code mutation detected by mutmut:
# 
# --- tests/deadcode.py
# +++ tests/deadcode.py
# @@ -305,7 +305,7 @@
#              cnd = self.static_value(node.test, deadcode)
#  
#              self.check_stmts(node.body, deadcode or cnd is False)
# -            else_is_dead = self.check_stmts(node.orelse, deadcode or cnd is True)
# +            else_is_dead = self.check_stmts(node.orelse, deadcode or cnd is False)
#  
#              if cnd is True and not contains_break(node):
#                  # while True: ... no break
# 

while True:
    pass
else:
    SSHException