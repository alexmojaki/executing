# This sample was generated for the following code mutation detected by mutmut:
# 
# --- tests/deadcode.py
# +++ tests/deadcode.py
# @@ -246,7 +246,7 @@
#  
#              self.walk_deadcode(node.test, deadcode)
#  
# -            deadcode = if_is_dead and else_is_dead
# +            deadcode = if_is_dead or else_is_dead
#  
#          elif isinstance(node, ast.Match):
#              self.walk_deadcode(node.subject, deadcode)
# 

def before_stmt(self, node, frame):
    if frame:
        return
    isinstance