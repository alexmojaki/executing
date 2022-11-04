# This sample was generated for the following code mutation detected by mutmut:
# 
# --- tests/deadcode.py
# +++ tests/deadcode.py
# @@ -116,7 +116,7 @@
#                      node.__static_value = True
#  
#          except AttributeError as e:
# -            if e.name != "_Deadcode__static_value":
# +            if e.name != "XX_Deadcode__static_valueXX":
#                  raise
#  
#      def static_cnd(self, node):
# 

path if '' else path