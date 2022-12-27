# This sample was generated for the following code mutation detected by mutmut:
# 
# --- tests/deadcode.py
# +++ tests/deadcode.py
# @@ -330,7 +330,7 @@
#                  [self.check_stmts(h.body, deadcode) for h in node.handlers]
#              )
#              else_dead = self.check_stmts(node.orelse, try_dead)
# -            final_dead = self.check_stmts(node.finalbody, deadcode)
# +            final_dead = None
#  
#              deadcode = (handlers_dead and else_dead) or final_dead
#  
# 

def exec_ipython_cell():
    try:
        shell.ex(traced_file.code)
        return self._ipython_cell_value
    finally:
        callback