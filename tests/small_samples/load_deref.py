# VerifierFailure:
# ast.Name is not created from LOAD_DEREF

# instruction: Instruction(opname='LOAD_DEREF', opcode=137, arg=2, argval='_TVMScriptParser__convert_index', argrepr='_TVMScriptParser__convert_index', offset=12, starts_line=None, is_jump_target=False, positions=Positions(lineno=22, end_lineno=22, col_offset=9, end_col_offset=24))

# node: Name(id='__convert_index', ctx=Load(), lineno=22, col_offset=9, end_lineno=22, end_col_offset=24)

class TVMScriptParser:

    def transform_SubscriptAssign():

        def __convert_index():
            pass
        [__convert_index for x in indexes]
