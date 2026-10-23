"""Комнаты в Redis (hash с TTL), приглашение ссылкой и события через pub/sub."""
import asyncio
import json
import re

from redis.asyncio import Redis

ROOM_TTL = 1800
ROOM_ID = re.compile(r"[A-Za-z0-9_-]{1,32}")


def rkey(room_id: str) -> str:
    return f"room:{room_id}"


async def create_room(r: Redis, room_id: str, game: str, players: list[str], ttl: int = ROOM_TTL) -> None:
    key = rkey(room_id)
    if not await r.hsetnx(key, "game", game):
        raise ValueError(f"комната {room_id} уже есть")
    await r.hset(key, mapping={"players": json.dumps(players, ensure_ascii=False), "state": "{}"})
    await r.expire(key, ttl)


async def load_room(r: Redis, room_id: str) -> dict | None:
    data = await r.hgetall(rkey(room_id))
    if not data:
        return None
    return {"game": data["game"], "players": json.loads(data["players"]), "state": json.loads(data["state"])}


async def save_state(r: Redis, room_id: str, state: dict, ttl: int = ROOM_TTL) -> None:
    key = rkey(room_id)
    if not await r.exists(key):
        raise LookupError(room_id)
    async with r.pipeline(transaction=True) as pipe:
        pipe.hset(key, "state", json.dumps(state, ensure_ascii=False))
        pipe.expire(key, ttl)          # активная комната живёт дольше
        await pipe.execute()


def invite_link(bot_username: str, room_id: str) -> str:
    """Ссылка, открывающая Mini App сразу в комнате: параметр startapp придёт в initData как start_param."""
    if not ROOM_ID.fullmatch(room_id):
        raise ValueError("room_id: латиница, цифры, _ и -, до 32 символов (держим ссылку короткой)")
    return f"https://t.me/{bot_username.lstrip('@')}?startapp=room_{room_id}"


def room_from_start_param(start_param: str | None) -> str | None:
    if not start_param or not start_param.startswith("room_"):
        return None
    room_id = start_param[5:]
    return room_id if ROOM_ID.fullmatch(room_id) else None


async def publish(r: Redis, room_id: str, message: dict) -> int:
    """Разослать событие всем копиям сервера, подписанным на комнату. Возвращает число подписчиков."""
    return await r.publish(f"events:{room_id}", json.dumps(message, ensure_ascii=False))


async def collect(r: Redis, room_id: str, n: int, timeout: float = 2.0) -> list[dict]:
    """Подписаться на события комнаты и вернуть первые n сообщений (или сколько успело прийти)."""
    out: list[dict] = []
    pubsub = r.pubsub()
    await pubsub.subscribe(f"events:{room_id}")
    try:
        async with asyncio.timeout(timeout):
            while len(out) < n:
                msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=0.05)
                if msg is not None:
                    out.append(json.loads(msg["data"]))
    except TimeoutError:
        pass
    finally:
        await pubsub.unsubscribe()
        await pubsub.aclose()
    return out
