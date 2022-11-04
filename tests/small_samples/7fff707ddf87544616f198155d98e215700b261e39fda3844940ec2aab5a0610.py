# This sample was generated for the following code mutation detected by mutmut:
# 
# --- tests/deadcode.py
# +++ tests/deadcode.py
# @@ -332,7 +332,7 @@
#              else_dead = self.check_stmts(node.orelse, try_dead)
#              final_dead = self.check_stmts(node.finalbody, deadcode)
#  
# -            deadcode = (handlers_dead and else_dead) or final_dead
# +            deadcode = (handlers_dead or else_dead) or final_dead
#  
#          elif isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And):
#              dead_op = deadcode
# 

def for_filename():
    try:
        return source_cache[filename]
    except KeyError:
        pass
    linecache