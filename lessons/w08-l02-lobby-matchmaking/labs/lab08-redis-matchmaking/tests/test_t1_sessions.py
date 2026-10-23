from sessions import create_session, drop_session, get_session


async def test_create_and_get(r):
    token = await create_session(r, 51234567)
    assert isinstance(token, str) and len(token) >= 32
    assert await get_session(r, token) == 51234567
    assert 3590 <= await r.ttl(f"session:{token}") <= 3600


async def test_tokens_unique(r):
    tokens = {await create_session(r, 1) for _ in range(50)}
    assert len(tokens) == 50


async def test_unknown(r):
    assert await get_session(r, "nope") is None


async def test_sliding_ttl(r):
    token = await create_session(r, 7, ttl=600)
    await r.expire(f"session:{token}", 5)          # «прошло» почти 10 минут
    assert await get_session(r, token, ttl=600) == 7
    assert await r.ttl(f"session:{token}") > 500   # обращение продлило сессию


async def test_drop(r):
    token = await create_session(r, 7)
    assert await drop_session(r, token) is True
    assert await get_session(r, token) is None
    assert await drop_session(r, token) is False
