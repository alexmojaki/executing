from .utils import tester

# tester calls tested with test_tester at global scope

assert tester([1, 2, 3]) == [1, 2, 3]

assert tester.asd is tester
assert tester[1 + 2] is tester
assert tester**4 is tester
assert tester * 3 is tester
assert tester - 2 is tester
assert tester + 1 is tester
assert -tester is +tester is ~tester is tester
assert (tester < 7) is tester
assert (tester >= 78) is tester
assert (tester != 79) is tester
# assert (5 != tester != 6) is tester
assert tester.foo(45, False) == 45

assert (tester or 234) == 234
assert (tester and 1123) is tester
