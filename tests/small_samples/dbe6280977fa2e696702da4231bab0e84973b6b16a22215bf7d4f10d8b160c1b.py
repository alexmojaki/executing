# This sample was generated for the following code mutation detected by mutmut:
# 
# --- tests/deadcode.py
# +++ tests/deadcode.py
# @@ -202,7 +202,7 @@
#                  self.walk_deadcode(node.msg, deadcode)
#                  deadcode = True
#  
# -            elif cnd is True:
# +            elif cnd is not True:
#                  node.deadcode = deadcode
#                  self.walk_deadcode(node.msg, True)
#  
# 

assert isinstance, (node,)