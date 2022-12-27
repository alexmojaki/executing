# This sample was generated for the following code mutation detected by mutmut:
# 
# --- executing/_position_node_finder.py
# +++ executing/_position_node_finder.py
# @@ -558,7 +558,7 @@
#          node_ctx = getattr(node, "ctx", None)
#  
#          ctx_match = (
# -            ctx is not type(None)
# +            ctx is  type(None)
#              or not hasattr(node, "ctx")
#              or isinstance(node_ctx, ctx)
#          )
# 

self.step_count += 1