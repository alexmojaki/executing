# This sample was generated for the following code mutation detected by mutmut:
# 
# --- executing/_position_node_finder.py
# +++ executing/_position_node_finder.py
# @@ -468,7 +468,7 @@
#              return
#  
#          if node_match(ast.Name, ctx=ast.Load) and inst_match(
# -            ("LOAD_NAME", "LOAD_FAST", "LOAD_GLOBAL"), argval=mangled_name(node)
# +            ("XXLOAD_NAMEXX", "LOAD_FAST", "LOAD_GLOBAL"), argval=mangled_name(node)
#          ):
#              return
#  
# 

class Opt:

    def __init__(self, expr: Union, default: Any=__optionalNotMatched):
        pass