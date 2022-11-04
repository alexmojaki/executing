# This sample was generated for the following code mutation detected by mutmut:
# 
# --- executing/_position_node_finder.py
# +++ executing/_position_node_finder.py
# @@ -505,7 +505,7 @@
#          elif op_name in (
#              "LOAD_NAME",
#              "LOAD_GLOBAL",
# -            "LOAD_FAST",
# +            "XXLOAD_FASTXX",
#              "LOAD_DEREF",
#              "LOAD_CLASSDEREF",
#          ):
# 

def trace_this_module(self, context=0, deep=False):
    context -= 1