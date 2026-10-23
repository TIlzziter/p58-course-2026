"""Очередь матчмейкинга на sorted set: участник — имя, score — рейтинг."""
from redis.asyncio import Redis


def qkey(game: str) -> str:
    return f"mm:{game}"


async def enqueue(r: Redis, game: str, player: str, rating: int) -> bool:
    """True, если игрок встал в очередь; False, если уже стоял (рейтинг не меняем)."""
    return await r.zadd(qkey(game), {player: rating}, nx=True) == 1


async def dequeue(r: Redis, game: str, player: str) -> bool:
    return await r.zrem(qkey(game), player) == 1


async def queue_size(r: Redis, game: str) -> int:
    return await r.zcard(qkey(game))


def allowed_diff(waited: float) -> int:
    """Допустимая разница рейтингов растёт с ожиданием: 100, +50 за каждые полные 10 с, не больше 400."""
    return min(100 + 50 * int(waited // 10), 400)


async def find_match(r: Redis, game: str, player: str, max_diff: int) -> str | None:
    """Ближайший по рейтингу соперник (при равенстве — меньшее имя). Оба уходят из очереди атомарно."""
    key = qkey(game)
    rating = await r.zscore(key, player)
    if rating is None:
        raise LookupError(player)
    found = await r.zrangebyscore(key, rating - max_diff, rating + max_diff, withscores=True)
    candidates = [(abs(score - rating), name, score) for name, score in found if name != player]
    if not candidates:
        return None
    _, opponent, opp_rating = min(candidates)
    async with r.pipeline(transaction=True) as pipe:
        pipe.zrem(key, player)
        pipe.zrem(key, opponent)
        removed_me, removed_opp = await pipe.execute()
    if removed_me and removed_opp:
        return opponent
    # Кого-то уже забрала другая копия сервера — возвращаем на место того, кого успели вынуть.
    if removed_me:
        await r.zadd(key, {player: rating})
    if removed_opp:
        await r.zadd(key, {opponent: opp_rating})
    return None
