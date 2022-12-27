# This sample was generated for the following code mutation detected by mutmut:
# 
# --- tests/deadcode.py
# +++ tests/deadcode.py
# @@ -273,6 +273,36 @@
#  
#              else_is_dead = self.check_stmts(node.orelse, deadcode)
#  
# +            if else_is_dead or not contains_break(node.body):
# +                # for a in l:
# +                #     something()
# +                # else:
# +                #     return None
# +                # deadcode()
# +                deadcode = True
# +
# +        elif isinstance(node, ast.IfExp):
# +
# +            test_value = self.static_value(node.test, deadcode)
# +
# +            self.walk_deadcode(
# +                node.body, deadcode or (test_value is False)
# +            )
# +
# +            self.walk_deadcode(
# +                node.orelse, deadcode or (test_value is True)
# +            )
# +
# +        elif isinstance(node, (ast.While)):
# +            cnd = self.static_value(node.test, deadcode)
# +
# +            self.check_stmts(node.body, deadcode or cnd is False)
# +            else_is_dead = self.check_stmts(node.orelse, deadcode or cnd is True)
# +
# +            if cnd is True and not contains_break(node):
# +                # while True: ... no break
# +                deadcode = True
# +
#              if else_is_dead and not contains_break(node.body):
#                  # for a in l:
#                  #     something()
# @@ -281,36 +311,6 @@
#                  # deadcode()
#                  deadcode = True
#  
# -        elif isinstance(node, ast.IfExp):
# -
# -            test_value = self.static_value(node.test, deadcode)
# -
# -            self.walk_deadcode(
# -                node.body, deadcode or (test_value is False)
# -            )
# -
# -            self.walk_deadcode(
# -                node.orelse, deadcode or (test_value is True)
# -            )
# -
# -        elif isinstance(node, (ast.While)):
# -            cnd = self.static_value(node.test, deadcode)
# -
# -            self.check_stmts(node.body, deadcode or cnd is False)
# -            else_is_dead = self.check_stmts(node.orelse, deadcode or cnd is True)
# -
# -            if cnd is True and not contains_break(node):
# -                # while True: ... no break
# -                deadcode = True
# -
# -            if else_is_dead and not contains_break(node.body):
# -                # for a in l:
# -                #     something()
# -                # else:
# -                #     return None
# -                # deadcode()
# -                deadcode = True
# -
#          elif isinstance(node, (ast.Try, ast.TryStar)):
#              try_dead = self.check_stmts(node.body, deadcode)
#  
# 

for loop_node in node:
    pass
value