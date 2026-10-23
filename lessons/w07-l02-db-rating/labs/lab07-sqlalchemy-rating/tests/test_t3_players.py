from sqlalchemy import func, select

import repo
from models import Player


async def test_create(session):
    p = await repo.get_or_create_player(session, 42, "Аня")
    assert p.id is not None and p.rating == 1000 and p.name == "Аня"


async def test_same_player_once(session):
    a = await repo.get_or_create_player(session, 42, "Аня")
    await session.commit()
    b = await repo.get_or_create_player(session, 42, "Аня")
    await session.commit()
    assert a.id == b.id
    assert await session.scalar(select(func.count()).select_from(Player)) == 1


async def test_name_updated(session):
    await repo.get_or_create_player(session, 42, "Аня")
    await session.commit()
    p = await repo.get_or_create_player(session, 42, "Анна")
    await session.commit()
    assert p.name == "Анна"
    assert await session.scalar(select(Player.name).where(Player.tg_id == 42)) == "Анна"


async def test_different_players(session):
    a = await repo.get_or_create_player(session, 1, "Аня")
    b = await repo.get_or_create_player(session, 2, "Аня")
    assert a.id != b.id
