from matchmaking import dequeue, enqueue, queue_size


async def test_enqueue(r):
    assert await enqueue(r, "c4", "Аня", 1200) is True
    assert await enqueue(r, "c4", "Боря", 1500) is True
    assert await queue_size(r, "c4") == 2
    assert await r.zscore("mm:c4", "Аня") == 1200


async def test_no_duplicates(r):
    await enqueue(r, "c4", "Аня", 1200)
    assert await enqueue(r, "c4", "Аня", 1300) is False
    assert await queue_size(r, "c4") == 1
    assert await r.zscore("mm:c4", "Аня") == 1200   # рейтинг не перезаписали


async def test_games_separate(r):
    await enqueue(r, "c4", "Аня", 1200)
    await enqueue(r, "snake", "Аня", 1000)
    assert await queue_size(r, "c4") == 1 and await queue_size(r, "snake") == 1


async def test_dequeue(r):
    await enqueue(r, "c4", "Аня", 1200)
    assert await dequeue(r, "c4", "Аня") is True
    assert await dequeue(r, "c4", "Аня") is False
    assert await queue_size(r, "c4") == 0
