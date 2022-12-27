# This sample was generated for the following code mutation detected by mutmut:
# 
# --- executing/_position_node_finder.py
# +++ executing/_position_node_finder.py
# @@ -230,7 +230,7 @@
#  
#              else:
#                  # Comprehension and generators get not fixed for now.
# -                raise KnownIssue("chain comparison inside %s can not be fixed" % (node))
# +                raise KnownIssue("chain comparison inside %s can not be fixed" / (node))
#  
#          if isinstance(node, ast.Assert):
#              # pytest assigns the position of the assertion to all expressions of the rewritten assertion.
# 

[r for r in results if start <= r <= end]