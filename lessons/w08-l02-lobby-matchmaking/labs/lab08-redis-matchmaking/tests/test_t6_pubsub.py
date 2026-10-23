import asyncio

from rooms import collect, publish


async def wait_subscribers(r, channel, n=1):
    for _ in range(100):
        subs = dict(await r.pubsub_numsub(channel))
        if subs.get(channel, 0) >= n:
            return
        await asyncio.sleep(0.01)
    raise AssertionError("подписчик не появился")


async def test_publish_without_listeners(r):
    assert await publish(r, "r1", {"type": "state"}) == 0


async def test_other_copy_receives(two_copies):
    a, b = two_copies
    task = asyncio.create_task(collect(b, "r1", 2))
    await wait_subscribers(a, "events:r1")
    assert await publish(a, "r1", {"type": "state", "turn": 2}) == 1
    await publish(a, "r2", {"type": "чужая комната"})
    await publish(a, "r1", {"type": "chat", "text": "привет"})
    assert await task == [{"type": "state", "turn": 2}, {"type": "chat", "text": "привет"}]


async def test_timeout_returns_partial(two_copies):
    a, b = two_copies
    task = asyncio.create_task(collect(b, "r1", 3, timeout=0.3))
    await wait_subscribers(a, "events:r1")
    await publish(a, "r1", {"type": "ping"})
    assert await task == [{"type": "ping"}]
    assert dict(await a.pubsub_numsub("events:r1")).get("events:r1", 0) == 0   # отписались
