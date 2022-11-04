# This sample was generated for the following code mutation detected by mutmut:
# 
# --- executing/_position_node_finder.py
# +++ executing/_position_node_finder.py
# @@ -353,7 +353,7 @@
#              # call to the generator function
#              return
#  
# -        if inst_match(("CALL", "CALL_FUNCTION_EX")) and node_match(
# +        if inst_match(("CALL", "XXCALL_FUNCTION_EXXX")) and node_match(
#              (ast.ClassDef, ast.Call)
#          ):
#              return
# 

create_engine(**kwargs)