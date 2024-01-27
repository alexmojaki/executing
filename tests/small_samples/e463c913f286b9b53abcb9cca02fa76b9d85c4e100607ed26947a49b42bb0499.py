def __call__(func):

    async def inner():
        func