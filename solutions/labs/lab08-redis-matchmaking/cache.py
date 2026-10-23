"""Кэш «прочитал — нет — посчитал — положил» (cache-aside) для таблицы лидеров."""
import json
from collections.abc import Awaitable, Callable

from redis.asyncio import Redis


async def cached(r: Redis, key: str, ttl: int, compute: Callable[[], Awaitable]):
    raw = await r.get(f"cache:{key}")
    if raw is not None:
        return json.loads(raw)
    value = await compute()
    await r.set(f"cache:{key}", json.dumps(value, ensure_ascii=False), ex=ttl)
    return value


async def invalidate(r: Redis, key: str) -> None:
    await r.delete(f"cache:{key}")
