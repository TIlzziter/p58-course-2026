import asyncio

import pytest
from game.matchmaker import Matchmaker


async def test_pair():
    mm = Matchmaker(size=2, timeout=1)
    a = asyncio.create_task(mm.find("ann"))
    await asyncio.sleep(0)
    assert mm.waiting() == ["ann"]
    b = asyncio.create_task(mm.find("bob"))
    assert await a == ["ann", "bob"] and await b == ["ann", "bob"]
    assert mm.waiting() == []


async def test_groups_of_three_in_order():
    mm = Matchmaker(size=3, timeout=1)
    tasks = [asyncio.create_task(mm.find(u)) for u in ["a", "b", "c", "d"]]
    first = await asyncio.gather(*tasks[:3])
    assert first == [["a", "b", "c"]] * 3
    assert mm.waiting() == ["d"]
    tasks[3].cancel()


async def test_timeout_leaves_queue():
    mm = Matchmaker(size=2, timeout=0.05)
    with pytest.raises(TimeoutError):
        await mm.find("ann")
    assert mm.waiting() == []
    # после таймаута пара собирается с новыми игроками
    mm.timeout = 1
    r = await asyncio.gather(mm.find("bob"), mm.find("cat"))
    assert r == [["bob", "cat"], ["bob", "cat"]]


async def test_duplicate():
    mm = Matchmaker(size=2, timeout=1)
    t = asyncio.create_task(mm.find("ann"))
    await asyncio.sleep(0)
    with pytest.raises(ValueError):
        await mm.find("ann")
    assert mm.waiting() == ["ann"]
    assert mm.cancel("ann") is True and mm.cancel("ann") is False
    t.cancel()
