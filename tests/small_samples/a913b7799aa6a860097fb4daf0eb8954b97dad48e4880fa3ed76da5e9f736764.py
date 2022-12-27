# This sample was generated for the following code mutation detected by mutmut:
# 
# --- executing/_position_node_finder.py
# +++ executing/_position_node_finder.py
# @@ -262,7 +262,7 @@
#      @staticmethod
#      def is_except_cleanup(inst: dis.Instruction, node: EnhancedAST) -> bool:
#          if inst.opname not in (
# -            "STORE_NAME",
# +            "XXSTORE_NAMEXX",
#              "STORE_FAST",
#              "STORE_DEREF",
#              "STORE_GLOBAL",
# 

try:
    from aiohttp import web
    import aiohttp_cors
except ImportError as ie:
    pass