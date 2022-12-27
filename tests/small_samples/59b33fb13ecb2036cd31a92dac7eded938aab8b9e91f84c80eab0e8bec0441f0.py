# This sample was generated for the following code mutation detected by mutmut:
# 
# --- tests/deadcode.py
# +++ tests/deadcode.py
# @@ -204,7 +204,7 @@
#  
#              elif cnd is True:
#                  node.deadcode = deadcode
# -                self.walk_deadcode(node.msg, True)
# +                self.walk_deadcode(node.msg, False)
#  
#              else:
#                  node.deadcode = deadcode
# 

assert '/recipe-release%2F0.6.1', client