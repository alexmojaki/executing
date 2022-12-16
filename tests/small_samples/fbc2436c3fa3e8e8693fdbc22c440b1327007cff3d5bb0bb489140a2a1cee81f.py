async def test_contextmanager_except():
    async with woohoo as x:
        pass
    self