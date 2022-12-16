with _winreg:
    for subkeyname in enum_types:
        try:
            with _winreg:
                continue
        except OSError:
            pass