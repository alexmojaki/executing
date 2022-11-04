# This sample was generated for the following code mutation detected by mutmut:
# 
# --- tests/deadcode.py
# +++ tests/deadcode.py
# @@ -177,7 +177,7 @@
#                      if stmt.module == "__future__" and any(
#                          "annotations" == alias.name for alias in stmt.names
#                      ):
# -                        self.future_annotations = True
# +                        self.future_annotations = None
#  
#              self.check_stmts(node.body, deadcode)
#          elif isinstance(node, (ast.With, ast.AsyncWith)):
# 

from __future__ import annotations, with_statement

async def _start(self: Cloud) -> Cloud[IsAsynchronous]:
    pass