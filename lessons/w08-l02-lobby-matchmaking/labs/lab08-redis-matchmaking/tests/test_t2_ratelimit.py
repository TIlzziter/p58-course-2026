from sessions import allow


async def test_limit(r):
    results = [await allow(r, "user:1", 3, 10) for _ in range(5)]
    assert results == [True, True, True, False, False]


async def test_keys_independent(r):
    for _ in range(3):
        await allow(r, "user:1", 3, 10)
    assert await allow(r, "user:2", 3, 10) is True


async def test_ttl_set_once(r):
    await allow(r, "user:1", 5, 10)
    assert 1 <= await r.ttl("rl:user:1") <= 10
    await r.expire("rl:user:1", 3)                 # окно скоро закончится
    await allow(r, "user:1", 5, 10)
    assert await r.ttl("rl:user:1") <= 3           # новый запрос НЕ продлевает окно


async def test_new_window(r):
    for _ in range(4):
        await allow(r, "u", 3, 10)
    await r.delete("rl:u")                         # окно истекло
    assert await allow(r, "u", 3, 10) is True
