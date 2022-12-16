print(1e+300 * 1e+300 * 0)

# tuple becomes a LOAD_CONST
print((1e+300 * 1e+300 * 0,5))

# complex numbers too
print(1e+300 * 1e+300 * 0+5j)


def nan_in_function():
    print(1e+300 * 1e+300 * 0)
