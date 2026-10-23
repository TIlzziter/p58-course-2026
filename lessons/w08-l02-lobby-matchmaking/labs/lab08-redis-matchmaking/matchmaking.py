"""Очередь матчмейкинга на sorted set: участник — имя, score — рейтинг (задачи 3–4)."""
from redis.asyncio import Redis


def qkey(game: str) -> str:
    return f"mm:{game}"


async def enqueue(r: Redis, game: str, player: str, rating: int) -> bool:
    """True, если игрок встал в очередь; False, если уже стоял (рейтинг не меняем)."""
    await r.zadd(qkey(game), {player: rating})
    return True


async def dequeue(r: Redis, game: str, player: str) -> bool:
    raise NotImplementedError


async def queue_size(r: Redis, game: str) -> int:
    return len(await r.zrange(qkey(game), 0, -1))


def allowed_diff(waited: float) -> int:
    """Допустимая разница рейтингов: 100, +50 за каждые полные 10 с ожидания, не больше 400."""
    raise NotImplementedError


async def find_match(r: Redis, game: str, player: str, max_diff: int) -> str | None:
    """Ближайший по рейтингу соперник (при равенстве — меньшее имя). Оба уходят из очереди атомарно."""
    raise NotImplementedError
