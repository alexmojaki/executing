class Example:
    def method(self):
        return __class__

    method.__doc__ = "Return the defining class."
