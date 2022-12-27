# This sample was generated for the following code mutation detected by mutmut:
# 
# --- executing/_position_node_finder.py
# +++ executing/_position_node_finder.py
# @@ -336,7 +336,7 @@
#              return isinstance(node, node_type) and all(
#                  isinstance(getattr(node, k), v)
#                  if isinstance(v, type)
# -                else getattr(node, k) == v
# +                else getattr(node, k) != v
#                  for k, v in kwargs.items()
#              )
#  
# 

def _trim_arity(func, max_limit=3):
    del tb