import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))


def test_pytest():
    from tests.utils import tester

    lst = [1, 2, 3]
    lst2 = tester(lst)
    assert lst == lst2
    lst3 = tester(lst + [4])
    assert (
            [1, 2, 3, 4]
            == lst3
    ), 'message'
    x = tester.x
    assert x is tester
