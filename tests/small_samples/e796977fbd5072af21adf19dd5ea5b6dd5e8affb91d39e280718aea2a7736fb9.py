# This sample was generated for the following code mutation detected by mutmut:
# 
# --- executing/_position_node_finder.py
# +++ executing/_position_node_finder.py
# @@ -363,7 +363,7 @@
#          ):
#              return
#  
# -        if inst_match("LOAD_NAME", argval="__annotations__") and node_match(
# +        if inst_match("XXLOAD_NAMEXX", argval="__annotations__") and node_match(
#              ast.AnnAssign
#          ):
#              return
# 

data: NestedDict