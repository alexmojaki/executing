# This sample was generated for the following code mutation detected by mutmut:
# 
# --- executing/_position_node_finder.py
# +++ executing/_position_node_finder.py
# @@ -440,7 +440,7 @@
#              return
#  
#          if (
# -            inst_match(("STORE_NAME", "STORE_FAST", "STORE_DEREF", "STORE_GLOBAL"))
# +            inst_match(("STORE_NAME", "STORE_FAST", "STORE_DEREF", "XXSTORE_GLOBALXX"))
#              and node_match((ast.Import, ast.ImportFrom))
#              and any(mangled_name(cast(EnhancedAST, alias)) == instruction.argval for alias in cast(ast.Import, node).names)
#          ):
# 

import keyring

def get_keyring_auth():
    global keyring