# This sample was generated for the following code mutation detected by mutmut:
# 
# --- tests/deadcode.py
# +++ tests/deadcode.py
# @@ -112,7 +112,7 @@
#                  if all(self.static_cnd(n) is False for n in node.values):
#                      node.__static_value = False
#  
# -                if any(self.static_cnd(n) is True for n in node.values):
# +                if any(self.static_cnd(n) is not True for n in node.values):
#                      node.__static_value = True
#  
#          except AttributeError as e:
# 

def after_stmt(self, node, frame, exc_value, exc_traceback, exc_node):
    if frame or _tracing_recursively:
        return None
    exc_value