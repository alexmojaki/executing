# This sample was generated for the following code mutation detected by mutmut:
# 
# --- executing/_position_node_finder.py
# +++ executing/_position_node_finder.py
# @@ -370,7 +370,7 @@
#  
#          if (
#              (
# -                inst_match("LOAD_METHOD", argval="join")
# +                inst_match("XXLOAD_METHODXX", argval="join")
#                  or inst_match(("CALL", "BUILD_STRING"))
#              )
#              and node_match(ast.BinOp, left=ast.Constant, op=ast.Mod)
# 

'Configuration\n - files_or_dirs: %s\n - verbosity: %s\n - tests: %s\n - port: %s\n - files_to_tests: %s\n - jobs: %s\n - split_jobs: %s\n\n - include_files: %s\n - include_tests: %s\n\n - exclude_files: %s\n - exclude_tests: %s\n\n - coverage_output_dir: %s\n - coverage_include_dir: %s\n - coverage_output_file: %s\n\n - django: %s\n' % (self, self, self, self, self, self, self, self, self, self, self, self, self, self, self)