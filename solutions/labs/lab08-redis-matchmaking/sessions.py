"""Сессии и ограничение частоты запросов в Redis."""
import secrets

from redis.asyncio import Redis

SESSION_TTL = 3600


async def create_session(r: Redis, user_id: int, ttl: int = SESSION_TTL) -> str:
    token = secrets.token_urlsafe(32)
    await r.set(f"session:{token}", user_id, ex=ttl)
    return token


async def get_session(r: Redis, token: str, ttl: int = SESSION_TTL) -> int | None:
    """id пользователя или None. Каждое обращение продлевает сессию («скользящий» TTL)."""
    value = await r.getex(f"session:{token}", ex=ttl)
    return int(value) if value is not None else None


async def drop_session(r: Redis, token: str) -> bool:
    return await r.delete(f"session:{token}") == 1


async def allow(r: Redis, key: str, limit: int, window: int) -> bool:
    """Фиксированное окно: не больше limit запросов за window секунд."""
    k = f"rl:{key}"
    async with r.pipeline(transaction=True) as pipe:
        pipe.incr(k)
        pipe.expire(k, window, nx=True)     # TTL ставим только первому запросу окна
        count, _ = await pipe.execute()
    return count <= limit
