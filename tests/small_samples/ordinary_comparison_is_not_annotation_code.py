# User-written code resembling an annotation header must still map to AST nodes.
def callback(format, /):
    if format > 2: raise NotImplementedError
