try:
    compiler_options = CompilerOptions(multi_file=self.multi_file, separate=self.separate)
    result = emitmodule.parse_and_typecheck(sources=sources, options=options, compiler_options=compiler_options, groups=groups, alt_lib_path='.')
    errors = Errors()
    (ir, cfiles) = emitmodule.compile_modules_to_c(result, compiler_options=compiler_options, errors=errors, groups=groups)
    if errors.num_errors:
        errors.flush_errors()
        assert False, 'Compile error'
except CompileError as e:
    assert False, 'Compile error'