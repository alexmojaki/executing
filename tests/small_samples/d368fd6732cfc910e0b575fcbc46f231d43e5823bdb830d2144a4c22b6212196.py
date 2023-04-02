with patch:

    def outer():

        @cache_decorator
        def inner():
            pass