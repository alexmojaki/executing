def __call__():

    async def inner():
        async with self:
            return func