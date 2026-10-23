import asyncio

from game.matchmaker import Matchmaker


async def test_pair():
    mm = Matchmaker(size=2, timeout=1)
    a, b = await asyncio.gather(mm.find("ann"), mm.find("bob"))
    assert set(a) == {"ann", "bob"}
