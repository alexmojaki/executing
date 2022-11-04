# This sample was generated for the following code mutation detected by mutmut:
# 
# --- executing/_position_node_finder.py
# +++ executing/_position_node_finder.py
# @@ -507,7 +507,7 @@
#              "LOAD_GLOBAL",
#              "LOAD_FAST",
#              "LOAD_DEREF",
# -            "LOAD_CLASSDEREF",
# +            "XXLOAD_CLASSDEREFXX",
#          ):
#              typ = ast.Name
#              ctx = ast.Load
# 

def __init__(self, out=None, prefix='', columns='time', overwrite=False, color=None, enabled=True, watch_extras=(), replace_watch_extras=None, formatter_class=DefaultFormatter):

    class ConfiguredTracer:
        self