import pytest
from models import Match, Player
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError


async def _insp(session, fn):
    conn = await session.connection()
    return await conn.run_sync(lambda c: fn(inspect(c)))


async def test_columns(session):
    players = await _insp(session, lambda i: {c["name"] for c in i.get_columns("players")})
    matches = await _insp(session, lambda i: {c["name"] for c in i.get_columns("matches")})
    assert players == {"id", "tg_id", "name", "rating", "created_at"}
    assert matches == {"id", "game", "player1_id", "player2_id", "result", "delta1", "delta2", "played_at"}


async def test_rating_default_and_created_at(session):
    p = Player(tg_id=10, name="Аня")
    session.add(p)
    await session.commit()
    await session.refresh(p)
    assert p.rating == 1000
    assert p.created_at is not None


async def test_tg_id_unique(session):
    session.add_all([Player(tg_id=10, name="Аня"), Player(tg_id=10, name="Клон")])
    with pytest.raises(IntegrityError):
        await session.commit()


async def _two(session):
    a, b = Player(tg_id=1, name="Аня"), Player(tg_id=2, name="Боря")
    session.add_all([a, b])
    await session.flush()
    return a, b


async def test_foreign_keys(session):
    a, _ = await _two(session)
    session.add(Match(game="c4", player1_id=a.id, player2_id=999, result="win1", delta1=0, delta2=0))
    with pytest.raises(IntegrityError):
        await session.commit()


@pytest.mark.parametrize("result, same", [("lose", False), ("win1", True)])
async def test_checks(session, result, same):
    a, b = await _two(session)
    session.add(Match(game="c4", player1_id=a.id, player2_id=a.id if same else b.id,
                      result=result, delta1=0, delta2=0))
    with pytest.raises(IntegrityError):
        await session.commit()


async def test_cascade_delete(session):
    a, b = await _two(session)
    session.add(Match(game="c4", player1_id=a.id, player2_id=b.id, result="draw", delta1=0, delta2=0))
    await session.commit()
    await session.execute(text("DELETE FROM players WHERE id = :id"), {"id": a.id})
    await session.commit()
    assert (await session.execute(text("SELECT count(*) FROM matches"))).scalar() == 0


async def test_indexes(session):
    indexed = await _insp(session, lambda i: {tuple(ix["column_names"]) for ix in i.get_indexes("matches")})
    assert {("player1_id",), ("player2_id",), ("played_at",)} <= indexed
