def outer(closed):
    other, closed = closed, 128

    def inner():
        return closed

    return other, inner
