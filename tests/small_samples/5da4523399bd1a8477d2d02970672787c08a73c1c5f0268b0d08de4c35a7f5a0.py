# This sample was generated for the following code mutation detected by mutmut:
# 
# --- tests/deadcode.py
# +++ tests/deadcode.py
# @@ -200,7 +200,7 @@
#              if cnd is False:
#                  node.deadcode = deadcode
#                  self.walk_deadcode(node.msg, deadcode)
# -                deadcode = True
# +                deadcode = None
#  
#              elif cnd is True:
#                  node.deadcode = deadcode
# 

assert False, 'Can this happen?'
nodes