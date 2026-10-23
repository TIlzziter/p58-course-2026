"""Сессии и ограничение частоты запросов в Redis (задачи 1–2)."""
import random

from redis.asyncio import Redis

SESSION_TTL = 3600


async def create_session(r: Redis, user_id: int, ttl: int = SESSION_TTL) -> str:
    token = str(random.randint(0, 10**6))               # BUG? такой токен можно угадать
    await r.set(f"session:{token}", user_id)            # TODO: сессия должна истекать
    return token


async def get_session(r: Redis, token: str, ttl: int = SESSION_TTL) -> int | None:
    """id пользователя или None. Каждое обращение продлевает сессию («скользящий» TTL)."""
    value = await r.get(f"session:{token}")
    return int(value) if value is not None else None


async def drop_session(r: Redis, token: str) -> bool:
    raise NotImplementedError


async def allow(r: Redis, key: str, limit: int, window: int) -> bool:
    """Фиксированное окно: не больше limit запросов за window секунд."""
    k = f"rl:{key}"
    count = await r.incr(k)
    await r.expire(k, window)            # BUG? что будет, если запросы идут каждую секунду?
    return count <= limit
