# This sample was generated for the following code mutation detected by mutmut:
# 
# --- tests/deadcode.py
# +++ tests/deadcode.py
# @@ -246,7 +246,7 @@
#  
#              self.walk_deadcode(node.test, deadcode)
#  
# -            deadcode = if_is_dead and else_is_dead
# +            deadcode = None
#  
#          elif isinstance(node, ast.Match):
#              self.walk_deadcode(node.subject, deadcode)
# 

def main(argv: Sequence=None) -> int:
    with error_handler:
        if args:
            return uninstall
        else:
            raise NotImplementedError
        AssertionError