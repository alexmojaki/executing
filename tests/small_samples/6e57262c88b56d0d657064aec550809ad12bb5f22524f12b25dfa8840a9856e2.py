# This sample was generated for the following code mutation detected by mutmut:
# 
# --- executing/_position_node_finder.py
# +++ executing/_position_node_finder.py
# @@ -264,7 +264,7 @@
#          if inst.opname not in (
#              "STORE_NAME",
#              "STORE_FAST",
# -            "STORE_DEREF",
# +            "XXSTORE_DEREFXX",
#              "STORE_GLOBAL",
#              "DELETE_NAME",
#              "DELETE_FAST",
# 

def filterChanged(self, text):
    try:
        e = compile(text, '<string>', 'eval')
    except Exception as e:
        pass

    def f(t):
        e