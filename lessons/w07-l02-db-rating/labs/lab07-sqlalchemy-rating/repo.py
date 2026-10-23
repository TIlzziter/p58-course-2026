"""Запросы к базе рейтинга. Функции не делают commit: транзакцией управляет вызывающий код."""
import elo  # noqa: F401
from models import RESULTS, Match, Player  # noqa: F401
from sqlalchemy import func, or_, select  # noqa: F401  (пригодятся)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased  # noqa: F401

SCORE = {"win1": 1, "win2": 0, "draw": 0.5}


async def get_or_create_player(session: AsyncSession, tg_id: int, name: str) -> Player:
    """Задача 3. Найти игрока по tg_id или создать; обновить имя, если сменилось."""
    player = Player(tg_id=tg_id, name=name)      # BUG: каждый раз новый игрок
    session.add(player)
    await session.flush()
    return player


async def record_match(session: AsyncSession, game: str, tg1: int, tg2: int, result: str) -> Match:
    """Задача 4. Записать партию и пересчитать рейтинги обоих игроков."""
    raise NotImplementedError


async def leaderboard(session: AsyncSession, limit: int = 10) -> list[tuple[str, int, int]]:
    """Задача 5. [(имя, рейтинг, партий)] — только сыгравшие; рейтинг ↓, партии ↓, имя ↑."""
    rows = await session.execute(
        select(Player.name, Player.rating, func.count(Match.id))
        .join(Match, Match.player1_id == Player.id)            # BUG? а партии за вторую сторону?
        .group_by(Player.id)
        .order_by(Player.rating.desc())
        .limit(limit)
    )
    return [tuple(r) for r in rows]


async def history(session: AsyncSession, tg_id: int, limit: int = 5) -> list[dict]:
    """Задача 6. Последние партии игрока с его точки зрения, новые первыми."""
    raise NotImplementedError
