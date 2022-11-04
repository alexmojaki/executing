# This sample was generated for the following code mutation detected by mutmut:
# 
# --- tests/deadcode.py
# +++ tests/deadcode.py
# @@ -195,7 +195,7 @@
#              deadcode = True
#  
#          elif isinstance(node, ast.Assert):
# -            cnd = self.static_value(node.test, deadcode)
# +            cnd = None
#  
#              if cnd is False:
#                  node.deadcode = deadcode
# 

assert end