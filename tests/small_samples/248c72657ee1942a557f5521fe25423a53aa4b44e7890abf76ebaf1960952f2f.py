# This sample was generated for the following code mutation detected by mutmut:
# 
# --- tests/deadcode.py
# +++ tests/deadcode.py
# @@ -279,7 +279,7 @@
#                  # else:
#                  #     return None
#                  # deadcode()
# -                deadcode = True
# +                deadcode = False
#  
#          elif isinstance(node, ast.IfExp):
#  
# 

def replace(self, string):
    for start, end, match in self:
        pass
    else:
        return False
    self