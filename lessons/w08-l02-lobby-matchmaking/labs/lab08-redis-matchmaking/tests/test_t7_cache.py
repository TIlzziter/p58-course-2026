from cache import cached, invalidate


async def test_cached(r):
    calls = []

    async def compute():
        calls.append(1)
        return [{"name": "Аня", "rating": 1016}]

    first = await cached(r, "top", 30, compute)
    second = await cached(r, "top", 30, compute)
    assert first == second == [{"name": "Аня", "rating": 1016}]
    assert len(calls) == 1
    assert 1 <= await r.ttl("cache:top") <= 30


async def test_invalidate(r):
    n = 0

    async def compute():
        nonlocal n
        n += 1
        return n

    assert await cached(r, "k", 30, compute) == 1
    await invalidate(r, "k")
    assert await cached(r, "k", 30, compute) == 2


async def test_falsy_values_cached(r):
    calls = []

    async def compute():
        calls.append(1)
        return []

    assert await cached(r, "empty", 30, compute) == []
    assert await cached(r, "empty", 30, compute) == []
    assert len(calls) == 1          # пустой список — тоже значение, а не «нет в кэше»
