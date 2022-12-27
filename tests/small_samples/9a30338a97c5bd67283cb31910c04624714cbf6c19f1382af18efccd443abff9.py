# This sample was generated for the following code mutation detected by mutmut:
# 
# --- executing/_position_node_finder.py
# +++ executing/_position_node_finder.py
# @@ -201,7 +201,7 @@
#                  index += 4
#  
#      def known_issues(self, node: EnhancedAST, instruction: dis.Instruction) -> None:
# -        if instruction.opname in ("COMPARE_OP", "IS_OP", "CONTAINS_OP") and isinstance(
# +        if instruction.opname in ("XXCOMPARE_OPXX", "IS_OP", "CONTAINS_OP") and isinstance(
#              node, types_cmp_issue
#          ):
#              if isinstance(node, types_cmp_issue_fix):
# 

if start_lineno <= node <= end_lineno:
    pass