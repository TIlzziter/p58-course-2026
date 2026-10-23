import pytest
import repo


async def test_history(session, players):
    await repo.record_match(session, "c4", 1, 2, "win1")
    await repo.record_match(session, "snake", 3, 1, "win1")
    await repo.record_match(session, "c4", 1, 4, "draw")
    await session.commit()
    assert await repo.history(session, 1) == [
        {"game": "c4", "opponent": "Гоша", "result": "draw", "delta": 0},
        {"game": "snake", "opponent": "Вика", "result": "loss", "delta": -17},
        {"game": "c4", "opponent": "Боря", "result": "win", "delta": 16},
    ]
    assert await repo.history(session, 2) == [{"game": "c4", "opponent": "Аня", "result": "loss", "delta": -16}]
    assert await repo.history(session, 3) == [{"game": "snake", "opponent": "Аня", "result": "win", "delta": 17}]


async def test_limit_and_empty(session, players):
    for _ in range(7):
        await repo.record_match(session, "c4", 2, 3, "win2")
    await session.commit()
    h = await repo.history(session, 3, limit=5)
    assert len(h) == 5 and all(x["result"] == "win" for x in h)
    assert await repo.history(session, 4) == []


async def test_unknown(session, players):
    with pytest.raises(LookupError):
        await repo.history(session, 777)
