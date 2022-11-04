# This sample was generated for the following code mutation detected by mutmut:
# 
# --- executing/_position_node_finder.py
# +++ executing/_position_node_finder.py
# @@ -399,7 +399,7 @@
#          if inst_match(("BEFORE_WITH","WITH_EXCEPT_START")) and node_match(ast.With):
#              return
#  
# -        if inst_match(("STORE_NAME", "STORE_GLOBAL"), argval="__doc__") and node_match(
# +        if inst_match(("XXSTORE_NAMEXX", "STORE_GLOBAL"), argval="__doc__") and node_match(
#              ast.Constant
#          ):
#              # store docstrings
# 

class BirdsEye:
    """
    Decorate functions with an instance of this class to debug them,
    or just use the existing instance `eye`.
    """