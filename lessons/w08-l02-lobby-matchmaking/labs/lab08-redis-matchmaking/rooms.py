"""Комнаты в Redis (hash с TTL), приглашение ссылкой и события через pub/sub (задачи 5–6)."""
import asyncio  # noqa: F401
import json
import re

from redis.asyncio import Redis

ROOM_TTL = 1800
ROOM_ID = re.compile(r"[A-Za-z0-9_-]{1,32}")


def rkey(room_id: str) -> str:
    return f"room:{room_id}"


async def create_room(r: Redis, room_id: str, game: str, players: list[str], ttl: int = ROOM_TTL) -> None:
    # BUG? комната должна быть hash, не перезаписываться и истекать
    await r.set(rkey(room_id), json.dumps({"game": game, "players": players, "state": {}}))


async def load_room(r: Redis, room_id: str) -> dict | None:
    raw = await r.get(rkey(room_id))
    return json.loads(raw) if raw else None


async def save_state(r: Redis, room_id: str, state: dict, ttl: int = ROOM_TTL) -> None:
    raise NotImplementedError


def invite_link(bot_username: str, room_id: str) -> str:
    """https://t.me/<бот>?startapp=room_<id>; бот можно передать с @."""
    raise NotImplementedError


def room_from_start_param(start_param: str | None) -> str | None:
    raise NotImplementedError


async def publish(r: Redis, room_id: str, message: dict) -> int:
    """Разослать событие в канал events:<room_id>. Возвращает число подписчиков."""
    raise NotImplementedError


async def collect(r: Redis, room_id: str, n: int, timeout: float = 2.0) -> list[dict]:
    """Подписаться на события комнаты и вернуть первые n сообщений (или сколько успело прийти за timeout)."""
    raise NotImplementedError
