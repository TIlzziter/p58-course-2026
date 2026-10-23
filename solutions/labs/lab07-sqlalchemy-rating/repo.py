"""Запросы к базе рейтинга. Функции не делают commit: транзакцией управляет вызывающий код."""
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

import elo
from models import RESULTS, Match, Player

SCORE = {"win1": 1, "win2": 0, "draw": 0.5}


async def get_or_create_player(session: AsyncSession, tg_id: int, name: str) -> Player:
    player = await session.scalar(select(Player).where(Player.tg_id == tg_id))
    if player is None:
        player = Player(tg_id=tg_id, name=name)
        session.add(player)
        await session.flush()          # получаем player.id и rating из базы
    elif player.name != name:
        player.name = name             # в Telegram имя могли сменить
    return player


async def _by_tg(session: AsyncSession, tg_id: int) -> Player:
    player = await session.scalar(select(Player).where(Player.tg_id == tg_id))
    if player is None:
        raise LookupError(f"нет игрока {tg_id}")
    return player


async def record_match(session: AsyncSession, game: str, tg1: int, tg2: int, result: str) -> Match:
    if result not in RESULTS:
        raise ValueError(f"неизвестный результат {result!r}")
    if tg1 == tg2:
        raise ValueError("игрок не может играть сам с собой")
    p1, p2 = await _by_tg(session, tg1), await _by_tg(session, tg2)
    new1, new2 = elo.update(p1.rating, p2.rating, SCORE[result])
    match = Match(game=game, player1_id=p1.id, player2_id=p2.id, result=result,
                  delta1=new1 - p1.rating, delta2=new2 - p2.rating)
    p1.rating, p2.rating = new1, new2
    session.add(match)
    await session.flush()
    return match


def _games_subquery():
    """Сколько партий сыграл каждый игрок (за любую сторону)."""
    return (
        select(Player.id.label("player_id"), func.count(Match.id).label("games"))
        .join(Match, or_(Match.player1_id == Player.id, Match.player2_id == Player.id))
        .group_by(Player.id)
        .subquery()
    )


async def leaderboard(session: AsyncSession, limit: int = 10) -> list[tuple[str, int, int]]:
    games = _games_subquery()
    rows = await session.execute(
        select(Player.name, Player.rating, games.c.games)
        .join(games, games.c.player_id == Player.id)
        .order_by(Player.rating.desc(), games.c.games.desc(), Player.name)
        .limit(limit)
    )
    return [tuple(r) for r in rows]


async def history(session: AsyncSession, tg_id: int, limit: int = 5) -> list[dict]:
    me = await _by_tg(session, tg_id)
    p1, p2 = aliased(Player), aliased(Player)
    rows = await session.execute(
        select(Match, p1.name, p2.name)
        .join(p1, Match.player1_id == p1.id)
        .join(p2, Match.player2_id == p2.id)
        .where(or_(Match.player1_id == me.id, Match.player2_id == me.id))
        .order_by(Match.played_at.desc(), Match.id.desc())
        .limit(limit)
    )
    out = []
    for match, name1, name2 in rows:
        first = match.player1_id == me.id
        if match.result == "draw":
            outcome = "draw"
        else:
            outcome = "win" if (match.result == "win1") == first else "loss"
        out.append({
            "game": match.game,
            "opponent": name2 if first else name1,
            "result": outcome,
            "delta": match.delta1 if first else match.delta2,
        })
    return out
