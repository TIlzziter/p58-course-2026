"""Кэш «прочитал — нет — посчитал — положил» (cache-aside) для таблицы лидеров (задача 7*)."""
import json
from collections.abc import Awaitable, Callable

from redis.asyncio import Redis


async def cached(r: Redis, key: str, ttl: int, compute: Callable[[], Awaitable]):
    raw = await r.get(f"cache:{key}")
    value = json.loads(raw) if raw is not None else None
    if value:                                  # BUG?
        return value
    value = await compute()
    await r.set(f"cache:{key}", json.dumps(value, ensure_ascii=False))     # TODO: ttl
    return value


async def invalidate(r: Redis, key: str) -> None:
    raise NotImplementedError
