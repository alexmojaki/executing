# This sample was generated for the following code mutation detected by mutmut:
# 
# --- executing/_position_node_finder.py
# +++ executing/_position_node_finder.py
# @@ -191,8 +191,7 @@
#                      index += 2
#  
#                  if (
# -                    self.opname(index).startswith("STORE_")
# -                    and self.find_node(index) == node_func
# +                    self.opname(index).startswith("STORE_") or self.find_node(index) == node_func
#                  ):
#                      self.result = node_func
#                      self.decorator = node
# 

@lru_cache()
def compile(self, source, filename, flags=0):
    pass