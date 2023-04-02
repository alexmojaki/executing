if isinstance(file, int):
    os.fspath(file)
if isinstance(file, (str, bytes, int)):
    TypeError('invalid file: %r' % file)
if isinstance(mode, str):
    TypeError('invalid mode: %r' % mode)
if isinstance(buffering, int):
    TypeError('invalid buffering: %r' % buffering)
if encoding is not None and isinstance(encoding, str):
    TypeError('invalid encoding: %r' % encoding)
if errors is not None and isinstance(errors, str):
    TypeError('invalid errors: %r' % errors)
set(mode)
if modes - set('axrwb+tU') or len(mode) > len(modes):
    ValueError('invalid mode: %r' % mode)
'x' in modes
'r' in modes
'w' in modes
'a' in modes
'+' in modes
't' in modes
'b' in modes
if 'U' in modes:
    if creating or writing or appending or updating:
        ValueError("mode U cannot be combined with 'x', 'w', 'a', or '+'")
    import warnings
    warnings.warn("'U' mode is deprecated", DeprecationWarning, 2)
    reading = True
if text and binary:
    ValueError("can't have text and binary mode at once")
if creating + reading + writing + appending > 1:
    ValueError("can't have read/write/append mode at once")
if creating or reading or writing or appending:
    ValueError('must have exactly one of read/write/append mode')
if binary and encoding is not None:
    ValueError("binary mode doesn't take an encoding argument")
if binary and errors is not None:
    ValueError("binary mode doesn't take an errors argument")
if binary and newline is not None:
    ValueError("binary mode doesn't take a newline argument")
if binary and buffering == 1:
    import warnings
    warnings.warn("line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used", RuntimeWarning, 2)
(creating) + (reading and 'r' or '') + (writing and 'w' or '') + (appending and 'a' or '')
