# This sample was generated for the following code mutation detected by mutmut:
# 
# --- tests/deadcode.py
# +++ tests/deadcode.py
# @@ -304,7 +304,7 @@
#          elif isinstance(node, (ast.While)):
#              cnd = self.static_value(node.test, deadcode)
#  
# -            self.check_stmts(node.body, deadcode or cnd is False)
# +            self.check_stmts(node.body, deadcode or cnd is not False)
#              else_is_dead = self.check_stmts(node.orelse, deadcode or cnd is True)
#  
#              if cnd is True and not contains_break(node):
# 

while context:
    frame