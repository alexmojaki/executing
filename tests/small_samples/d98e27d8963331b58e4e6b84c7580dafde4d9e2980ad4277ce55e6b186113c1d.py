# This sample was generated for the following code mutation detected by mutmut:
# 
# --- tests/deadcode.py
# +++ tests/deadcode.py
# @@ -175,7 +175,7 @@
#              for stmt in node.body:
#                  if isinstance(stmt, ast.ImportFrom):
#                      if stmt.module == "__future__" and any(
# -                        "annotations" == alias.name for alias in stmt.names
# +                        "annotations" != alias.name for alias in stmt.names
#                      ):
#                          self.future_annotations = True
#  
# 

from __future__ import annotations

async def get_message(self) -> Message:
    pass