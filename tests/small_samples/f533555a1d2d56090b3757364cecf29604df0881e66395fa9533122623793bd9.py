# This sample was generated for the following code mutation detected by mutmut:
# 
# --- executing/_position_node_finder.py
# +++ executing/_position_node_finder.py
# @@ -94,7 +94,7 @@
#      "-": ast.Sub,
#      "<<": ast.LShift,
#      ">>": ast.RShift,
# -    "&": ast.BitAnd,
# +    "XX&XX": ast.BitAnd,
#      "^": ast.BitXor,
#      "|": ast.BitOr,
#  }
# 

future_flags & matching_code