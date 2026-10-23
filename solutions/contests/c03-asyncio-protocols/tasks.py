"""Контест 3 — эталонные решения A–C."""
import asyncio
import json
from collections import Counter


# ---------- A. Протоколы ----------
def count_types(log: list[str]) -> dict[str, int]:
    """A1. Сколько сообщений каждого type; строки, которые не JSON-объект с type-строкой, — в "invalid"."""
    c = Counter()
    for line in log:
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            c["invalid"] += 1
            continue
        if isinstance(msg, dict) and isinstance(msg.get("type"), str):
            c[msg["type"]] += 1
        else:
            c["invalid"] += 1
    return dict(sorted(c.items()))


def split_stream(chunks: list[str]) -> list[str]:
    """A2. Сообщения разделены \\n, но приходят кусками как попало. Вернуть целые сообщения (без пустых)."""
    buf, out = "", []
    for ch in chunks:
        buf += ch
        *done, buf = buf.split("\n")
        out += [m for m in done if m]
    return out


def encode_frame(text: str) -> bytes:
    """A3. Кадр: длина в БАЙТАХ (2 байта, big-endian) + текст в UTF-8."""
    data = text.encode()
    if len(data) > 0xFFFF:
        raise ValueError("слишком длинное сообщение")
    return len(data).to_bytes(2, "big") + data


def decode_frames(data: bytes) -> list[str]:
    """A3. Разобрать подряд идущие кадры; неполный последний кадр отбросить."""
    out, i = [], 0
    while i + 2 <= len(data):
        n = int.from_bytes(data[i:i + 2], "big")
        if i + 2 + n > len(data):
            break
        out.append(data[i + 2:i + 2 + n].decode())
        i += 2 + n
    return out


# ---------- B. asyncio ----------
async def slow_double(x: int) -> int:
    """Дана: «медленный сервис» (не менять)."""
    await asyncio.sleep(0.1)
    return x * 2


async def double_all(xs: list[int]) -> list[int]:
    """B1. Все запросы конкурентно, результаты в исходном порядке."""
    return list(await asyncio.gather(*(slow_double(x) for x in xs)))


async def first_answer(delays: dict[str, float]) -> str:
    """B2. Игрок «отвечает» через delays[name] секунд. Вернуть имя первого, остальные задачи отменить."""
    async def answer(name: str) -> str:
        await asyncio.sleep(delays[name])
        return name

    tasks = [asyncio.create_task(answer(n)) for n in delays]
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    for t in pending:
        t.cancel()
    await asyncio.gather(*pending, return_exceptions=True)
    return min(done, key=lambda t: list(delays).index(t.result())).result()


async def with_timeout(coro, seconds: float, default=None):
    """B3. Результат корутины или default, если не уложилась."""
    try:
        async with asyncio.timeout(seconds):
            return await coro
    except TimeoutError:
        return default


async def limited(factories, limit: int) -> list:
    """B4*. factories — функции без аргументов, возвращающие корутины. Не больше limit одновременно; порядок сохранить."""
    sem = asyncio.Semaphore(limit)

    async def run(f):
        async with sem:
            return await f()

    return list(await asyncio.gather(*(run(f) for f in factories)))


# ---------- C. Комнаты ----------
def assign_rooms(players: list[str], size: int) -> tuple[list[list[str]], list[str]]:
    """C1. Рассадить по порядку прихода в комнаты по size; неполная последняя — в ожидание."""
    full = len(players) // size * size
    return [players[i:i + size] for i in range(0, full, size)], players[full:]


def max_online(events: list[tuple[int, str]]) -> int:
    """C2. events: (время, "in"/"out"). Максимум одновременно онлайн; в одно время сначала out, потом in."""
    cur = best = 0
    for _, kind in sorted(events, key=lambda e: (e[0], e[1] == "in")):
        cur += 1 if kind == "in" else -1
        best = max(best, cur)
    return best


def first_out_of_turn(moves: list[str], players: list[str]) -> int:
    """C3. Игроки ходят по кругу в порядке players. Индекс первого хода не в свою очередь или -1."""
    for i, who in enumerate(moves):
        if who != players[i % len(players)]:
            return i
    return -1


def matchmake(queue: list[tuple[str, int]], max_diff: int) -> list[tuple[str, str]]:
    """C4*. Пары из очереди (имя, рейтинг): по порядку очереди берём первого свободного и ищем ему
    первого свободного дальше по очереди с разницей рейтинга ≤ max_diff."""
    used, pairs = set(), []
    for i, (a, ra) in enumerate(queue):
        if a in used:
            continue
        for b, rb in queue[i + 1:]:
            if b not in used and abs(ra - rb) <= max_diff:
                used |= {a, b}
                pairs.append((a, b))
                break
    return pairs
