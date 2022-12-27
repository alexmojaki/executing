# This sample was generated for the following code mutation detected by mutmut:
# 
# --- tests/deadcode.py
# +++ tests/deadcode.py
# @@ -6,7 +6,7 @@
#      "search all child nodes except other loops for a break statement"
#  
#      if isinstance(node_or_list, ast.AST):
# -        childs = ast.iter_child_nodes(node_or_list)
# +        childs = None
#      elif isinstance(node_or_list, list):
#          childs = node_or_list
#      else:
# 

with self:
    for _ in tester:
        pass
    else:
        raise ValueError