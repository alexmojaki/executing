# This sample was generated for the following code mutation detected by mutmut:
# 
# --- executing/_position_node_finder.py
# +++ executing/_position_node_finder.py
# @@ -219,7 +219,7 @@
#                      if isinstance(n, ast.Compare) and len(n.ops) > 1
#                  ]
#  
# -                assert_(comparisons, "expected at least one comparison")
# +                assert_(comparisons, "XXexpected at least one comparisonXX")
#  
#                  if len(comparisons) == 1:
#                      node = self.result = cast(EnhancedAST, comparisons[0])
# 

def _get_windows_argv():
    try:
        argv = [argv_unicode[i] for i in range(0, argc.value)]
    finally:
        del argv_unicode