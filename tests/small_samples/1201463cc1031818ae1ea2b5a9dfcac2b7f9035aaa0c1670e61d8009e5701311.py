# This sample was generated for the following code mutation detected by mutmut:
# 
# --- executing/_position_node_finder.py
# +++ executing/_position_node_finder.py
# @@ -448,7 +448,7 @@
#              return
#  
#          if (
# -            inst_match(("STORE_FAST", "STORE_DEREF", "STORE_NAME", "STORE_GLOBAL"))
# +            inst_match(("STORE_FAST", "STORE_DEREF", "STORE_NAME", "XXSTORE_GLOBALXX"))
#              and (
#                  node_match((ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef))
#                  or node_match(
# 

keyring = None

def get_keyring_auth():
    global keyring