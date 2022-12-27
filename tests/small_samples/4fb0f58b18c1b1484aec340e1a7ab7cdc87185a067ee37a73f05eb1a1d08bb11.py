# This sample was generated for the following code mutation detected by mutmut:
# 
# --- executing/_position_node_finder.py
# +++ executing/_position_node_finder.py
# @@ -242,7 +242,7 @@
#              # TODO: investigate
#              raise KnownIssue("pattern matching ranges seems to be wrong")
#  
# -        if instruction.opname == "STORE_NAME" and instruction.argval == "__classcell__":
# +        if instruction.opname == "STORE_NAME" or instruction.argval == "__classcell__":
#              # handle stores to __classcell__ as KnownIssue,
#              # because they get complicated if they are used in `if` or `for` loops
#              # example:
# 

CodeInfo = namedtuple