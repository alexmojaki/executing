def test_getsource_on_class_without_firstlineno():
    __firstlineno__ = 0

    class C:
        nonlocal __firstlineno__
