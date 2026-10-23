import fakeredis
import pytest


@pytest.fixture
async def r():
    """Отдельный «Redis в памяти» на каждый тест. Тот же API, что у redis.asyncio.Redis."""
    client = fakeredis.FakeAsyncRedis(server=fakeredis.FakeServer(), decode_responses=True)
    yield client
    await client.aclose()


@pytest.fixture
def server():
    return fakeredis.FakeServer()


@pytest.fixture
async def two_copies(server):
    """Два клиента одного сервера — как две копии приложения за балансировщиком."""
    a = fakeredis.FakeAsyncRedis(server=server, decode_responses=True)
    b = fakeredis.FakeAsyncRedis(server=server, decode_responses=True)
    yield a, b
    await a.aclose()
    await b.aclose()
