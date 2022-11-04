# This sample was generated for the following code mutation detected by mutmut:
# 
# --- executing/_position_node_finder.py
# +++ executing/_position_node_finder.py
# @@ -473,7 +473,7 @@
#              return
#  
#          if node_match(ast.Name, ctx=ast.Del) and inst_match(
# -            ("DELETE_NAME", "DELETE_GLOBAL"), argval=mangled_name(node)
# +            ("XXDELETE_NAMEXX", "DELETE_GLOBAL"), argval=mangled_name(node)
#          ):
#              return
#  
# 

class SerializedDAG:
    del __get_constructor_defaults