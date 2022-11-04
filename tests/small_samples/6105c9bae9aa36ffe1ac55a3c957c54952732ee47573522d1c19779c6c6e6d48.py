# This sample was generated for the following code mutation detected by mutmut:
# 
# --- tests/deadcode.py
# +++ tests/deadcode.py
# @@ -95,7 +95,7 @@
#  
#              elif isinstance(node, ast.IfExp):
#                  cnd = self.static_cnd(node.test)
# -                if cnd is True:
# +                if cnd is False:
#                      node.__static_value = node.body.__static_value
#  
#                  elif cnd is False:
# 

if 0 if 1 else 2:
    print