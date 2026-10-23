import pytest
from sqlalchemy import select

import repo
from models import Match, Player


async def rating(session, tg):
    return await session.scalar(select(Player.rating).where(Player.tg_id == tg))


async def test_win(session, players):
    m = await repo.record_match(session, "c4", 1, 2, "win1")
    await session.commit()
    assert (m.delta1, m.delta2) == (16, -16)
    assert await rating(session, 1) == 1016 and await rating(session, 2) == 984
    saved = await session.scalar(select(Match))
    assert (saved.game, saved.result, saved.player1_id != saved.player2_id) == ("c4", "win1", True)


async def test_series(session, players):
    await repo.record_match(session, "c4", 1, 2, "win1")     # 1016 / 984
    m = await repo.record_match(session, "c4", 2, 1, "win2")  # Аня снова
    await session.commit()
    assert (m.delta1, m.delta2) == (-15, 15)
    assert await rating(session, 1) == 1031 and await rating(session, 2) == 969
    m = await repo.record_match(session, "c4", 3, 1, "draw")
    assert (m.delta1, m.delta2) == (1, -1)


async def test_persisted_in_other_session(sessions, players):
    async with sessions() as s:
        await repo.record_match(s, "c4", 3, 4, "win2")
        await s.commit()
    async with sessions() as s:
        assert await rating(s, 4) == 1016


async def test_errors(session, players):
    with pytest.raises(ValueError):
        await repo.record_match(session, "c4", 1, 2, "lose")
    with pytest.raises(ValueError):
        await repo.record_match(session, "c4", 1, 1, "draw")
    with pytest.raises(LookupError):
        await repo.record_match(session, "c4", 1, 99, "win1")
    await session.rollback()
    assert await rating(session, 1) == 1000
    assert await session.scalar(select(Match)) is None
