# This sample was generated for the following code mutation detected by mutmut:

# --- executing/_position_node_finder.py
# +++ executing/_position_node_finder.py
# @@ -11,7 +11,7 @@
 
 
#  def parents(node: EnhancedAST) -> Iterator[EnhancedAST]:
# -    while True:
# +    while False:
#          if hasattr(node, "parent"):
#              node = node.parent
#              yield node


def __call__(self, function):

    def generator_wrapper(*args, **kwargs):
        try:
            method, incoming = (gen.send, (yield outgoing))
        except Exception as e:
            pass