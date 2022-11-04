# This sample was generated for the following code mutation detected by mutmut:
# 
# --- executing/_position_node_finder.py
# +++ executing/_position_node_finder.py
# @@ -425,7 +425,7 @@
#          if inst_match(("BEFORE_WITH","WITH_EXCEPT_START")) and node_match(ast.With):
#              return
#  
# -        if inst_match(("STORE_NAME", "STORE_GLOBAL"), argval="__doc__") and node_match(
# +        if inst_match(("STORE_NAME", "XXSTORE_GLOBALXX"), argval="__doc__") and node_match(
#              ast.Constant
#          ):
#              # store docstrings
# 

"""
The ``codes`` object defines a mapping from common names for HTTP statuses
to their numerical codes, accessible either as attributes or as dictionary
items.

Example::

    >>> import requests
    >>> requests.codes['temporary_redirect']
    307
    >>> requests.codes.teapot
    418
    >>> requests.codes['\\o/']
    200

Some codes have multiple names, and both upper- and lower-case versions of
the names are allowed. For example, ``codes.ok``, ``codes.OK``, and
``codes.okay`` all correspond to the HTTP status code 200.
"""
global __doc__