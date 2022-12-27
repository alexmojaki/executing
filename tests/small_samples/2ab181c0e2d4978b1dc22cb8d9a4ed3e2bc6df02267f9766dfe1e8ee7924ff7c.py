# This sample was generated for the following code mutation detected by mutmut:
# 
# --- tests/deadcode.py
# +++ tests/deadcode.py
# @@ -36,27 +36,7 @@
#      def __init__(self):
#          self.future_annotations = False
#  
# -    operator_map = {
# -        # binary
# -        ast.Add: operator.add,
# -        ast.Sub: operator.sub,
# -        ast.Mult: operator.mul,
# -        ast.Div: operator.truediv,
# -        ast.FloorDiv: operator.floordiv,
# -        ast.Mod: operator.mod,
# -        ast.Pow: operator.pow,
# -        ast.LShift: operator.lshift,
# -        ast.RShift: operator.rshift,
# -        ast.BitOr: operator.or_,
# -        ast.BitXor: operator.xor,
# -        ast.BitAnd: operator.and_,
# -        ast.MatMult: operator.matmul,
# -        # unary
# -        ast.UAdd: operator.pos,
# -        ast.USub: operator.neg,
# -        ast.Not: operator.not_,
# -        ast.Invert: operator.invert,
# -    }
# +    operator_map = None
#  
#      def annotate_static_values(self, node):
#          for n in ast.iter_child_nodes(node):
# 

if not 'a':
    print