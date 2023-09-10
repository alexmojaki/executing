

async def __aenter__():
    try:
        return (await self.gen.__anext__())
    except StopAsyncIteration:
        pass
