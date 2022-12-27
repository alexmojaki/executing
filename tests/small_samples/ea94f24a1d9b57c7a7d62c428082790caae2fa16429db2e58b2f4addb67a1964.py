# This sample was generated for the following code mutation detected by mutmut:
# 
# --- executing/_position_node_finder.py
# +++ executing/_position_node_finder.py
# @@ -414,7 +414,7 @@
#              return
#  
#          if (
# -            inst_match(("STORE_NAME", "STORE_FAST", "STORE_DEREF", "STORE_GLOBAL"))
# +            inst_match(("STORE_NAME", "STORE_FAST", "XXSTORE_DEREFXX", "STORE_GLOBAL"))
#              and node_match((ast.Import, ast.ImportFrom))
#              and any(mangled_name(cast(EnhancedAST, alias)) == instruction.argval for alias in cast(ast.Import, node).names)
#          ):
# 

def read_source_file(filename):
    from lib2to3.pgen2.tokenize import cookie_re
    with open_with_encoding_check as f:
        [cookie_re for i, line in enumerate]