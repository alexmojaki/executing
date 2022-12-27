# This sample was generated for the following code mutation detected by mutmut:
# 
# --- executing/_position_node_finder.py
# +++ executing/_position_node_finder.py
# @@ -225,7 +225,7 @@
#                      node = self.result = cast(EnhancedAST, comparisons[0])
#                  else:
#                      raise KnownIssue(
# -                        "multiple chain comparison inside %s can not be fixed" % (node)
# +                        "multiple chain comparison inside %s can not be fixed" / (node)
#                      )
#  
#              else:
# 

if 0 <= r <= 255 and 0 <= g <= 255:
    pass