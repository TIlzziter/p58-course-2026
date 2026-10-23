import pytest

from matchmaking import allowed_diff, enqueue, find_match, queue_size


async def fill(r, people):
    for name, rating in people:
        await enqueue(r, "c4", name, rating)


@pytest.mark.parametrize("waited, diff", [(0, 100), (9.9, 100), (10, 150), (35, 250), (60, 400), (600, 400)])
def test_allowed_diff(waited, diff):
    assert allowed_diff(waited) == diff


async def test_closest(r):
    await fill(r, [("Аня", 1200), ("Боря", 1290), ("Вика", 1230), ("Гоша", 1100)])
    assert await find_match(r, "c4", "Аня", 100) == "Вика"
    assert await queue_size(r, "c4") == 2
    assert await r.zscore("mm:c4", "Аня") is None and await r.zscore("mm:c4", "Вика") is None


async def test_tie_by_name(r):
    await fill(r, [("Аня", 1200), ("Гоша", 1250), ("Боря", 1150)])
    assert await find_match(r, "c4", "Аня", 100) == "Боря"


async def test_nobody(r):
    await fill(r, [("Аня", 1200), ("Боря", 1500)])
    assert await find_match(r, "c4", "Аня", 100) is None
    assert await queue_size(r, "c4") == 2           # никто не потерялся
    assert await find_match(r, "c4", "Аня", 300) == "Боря"


async def test_boundary(r):
    await fill(r, [("Аня", 1200), ("Боря", 1300)])
    assert await find_match(r, "c4", "Аня", 100) == "Боря"   # ровно 100 — подходит


async def test_not_in_queue(r):
    with pytest.raises(LookupError):
        await find_match(r, "c4", "Аня", 100)


async def test_two_copies_no_double_match(two_copies):
    a, b = two_copies
    await fill(a, [("Аня", 1200), ("Боря", 1210), ("Вика", 1190)])
    first = await find_match(a, "c4", "Аня", 100)
    second = await find_match(b, "c4", "Боря" if first != "Боря" else "Вика", 100)
    assert first in {"Боря", "Вика"} and second is None   # остался один — пары нет
    assert await queue_size(a, "c4") == 1
