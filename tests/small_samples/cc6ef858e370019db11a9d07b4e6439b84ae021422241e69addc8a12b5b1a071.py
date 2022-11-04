# This sample was generated for the following code mutation detected by mutmut:
# 
# --- executing/_position_node_finder.py
# +++ executing/_position_node_finder.py
# @@ -535,7 +535,7 @@
#              ctx = ast.Load
#              extra_filter = lambda e: mangled_name(e) == instruction.argval
#          elif op_name in (
# -            "LOAD_NAME",
# +            "XXLOAD_NAMEXX",
#              "LOAD_GLOBAL",
#              "LOAD_FAST",
#              "LOAD_DEREF",
# 

@__has_required_azure
class AzureTest:
    pass