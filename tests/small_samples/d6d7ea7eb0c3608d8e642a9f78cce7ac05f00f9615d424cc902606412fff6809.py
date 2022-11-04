# This sample was generated for the following code mutation detected by mutmut:
# 
# --- tests/deadcode.py
# +++ tests/deadcode.py
# @@ -113,7 +113,7 @@
#                      node.__static_value = False
#  
#                  if any(self.static_cnd(n) is True for n in node.values):
# -                    node.__static_value = True
# +                    node.__static_value = None
#  
#          except AttributeError as e:
#              if e.name != "_Deadcode__static_value":
# 

if True or type:
    obj['Filter'] = []