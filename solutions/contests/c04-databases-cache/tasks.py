"""Контест 4 — эталонные решения задач A–D."""
import re
import sqlite3
import time  # noqa: F401

from redis.asyncio import Redis

SCHEMA = """
CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL, rating INTEGER NOT NULL DEFAULT 1000);
CREATE TABLE matches (id INTEGER PRIMARY KEY,
                      p1 INTEGER NOT NULL REFERENCES players(id),
                      p2 INTEGER NOT NULL REFERENCES players(id),
                      result TEXT NOT NULL CHECK (result IN ('win1', 'win2', 'draw')));
"""

# ---------- A. SQL ----------


def top_players(conn: sqlite3.Connection, n: int) -> list[tuple[str, int]]:
    return conn.execute("SELECT name, rating FROM players ORDER BY rating DESC, name LIMIT ?", (n,)).fetchall()


def games_count(conn: sqlite3.Connection) -> dict[str, int]:
    rows = conn.execute("""
        SELECT p.name, count(m.id)
        FROM players AS p LEFT JOIN matches AS m ON m.p1 = p.id OR m.p2 = p.id
        GROUP BY p.id ORDER BY p.name""").fetchall()
    return dict(rows)


def win_rate(conn: sqlite3.Connection, name: str) -> float | None:
    games, wins = conn.execute("""
        SELECT count(*),
               sum((m.p1 = p.id AND m.result = 'win1') OR (m.p2 = p.id AND m.result = 'win2'))
        FROM players AS p JOIN matches AS m ON m.p1 = p.id OR m.p2 = p.id
        WHERE p.name = ?""", (name,)).fetchone()
    return round(wins / games, 2) if games else None


def best_streak(conn: sqlite3.Connection, name: str) -> int:
    rows = conn.execute("""
        SELECT (m.p1 = p.id AND m.result = 'win1') OR (m.p2 = p.id AND m.result = 'win2')
        FROM players AS p JOIN matches AS m ON m.p1 = p.id OR m.p2 = p.id
        WHERE p.name = ? ORDER BY m.id""", (name,)).fetchall()
    best = cur = 0
    for (won,) in rows:
        cur = cur + 1 if won else 0
        best = max(best, cur)
    return best


# ---------- B. Рейтинг ----------


def elo_delta(ra: int, rb: int, score: float, k: int = 32) -> int:
    expected = 1 / (1 + 10 ** ((rb - ra) / 400))
    return round(k * (score - expected))


def replay(matches: list[tuple[str, str, str]], start: int = 1000) -> dict[str, int]:
    ratings: dict[str, int] = {}
    for a, b, result in matches:
        ra, rb = ratings.setdefault(a, start), ratings.setdefault(b, start)
        d = elo_delta(ra, rb, {"win1": 1, "win2": 0, "draw": 0.5}[result])
        ratings[a], ratings[b] = ra + d, rb - d
    return dict(sorted(ratings.items()))


def rank_with_ties(ratings: dict[str, int]) -> list[tuple[int, str]]:
    order = sorted(ratings.items(), key=lambda kv: (-kv[1], kv[0]))
    out, place = [], 0
    for i, (name, rating) in enumerate(order):
        if i == 0 or rating != order[i - 1][1]:
            place = i + 1
        out.append((place, name))
    return out


# ---------- C. Redis ----------


async def add_win(r: Redis, name: str) -> int:
    return int(await r.zincrby("wins", 1, name))


async def top_wins(r: Redis, n: int) -> list[tuple[str, int]]:
    rows = await r.zrange("wins", 0, -1, withscores=True)
    rows = sorted(rows, key=lambda x: (-x[1], x[0]))[:n]
    return [(name, int(score)) for name, score in rows]


async def remember_recent(r: Redis, user: str, item: str, limit: int = 5) -> list[str]:
    key = f"recent:{user}"
    async with r.pipeline(transaction=True) as pipe:
        pipe.lrem(key, 0, item)
        pipe.lpush(key, item)
        pipe.ltrim(key, 0, limit - 1)
        pipe.lrange(key, 0, -1)
        *_, items = await pipe.execute()
    return items


async def once(r: Redis, key: str, ttl: int) -> bool:
    return bool(await r.set(f"once:{key}", 1, nx=True, ex=ttl))


async def sliding_allow(r: Redis, key: str, limit: int, window: float, now: float) -> bool:
    k = f"sw:{key}"
    await r.zremrangebyscore(k, "-inf", now - window)
    if await r.zcard(k) >= limit:
        return False
    await r.zadd(k, {f"{now}:{await r.incr(k + ':seq')}": now})
    await r.expire(k, int(window) + 1)
    return True


# ---------- D. Схемы и миграции ----------

TABLE_RE = re.compile(r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)\s*\((.*?)\)\s*;", re.I | re.S)
CONSTRAINT_WORDS = {"PRIMARY", "FOREIGN", "UNIQUE", "CHECK", "CONSTRAINT"}


def _split_top(body: str) -> list[str]:
    parts, depth, cur = [], 0, ""
    for ch in body:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    return [p.strip() for p in parts if p.strip()]


def parse_ddl(sql: str) -> dict[str, list[str]]:
    out = {}
    for table, body in TABLE_RE.findall(sql):
        cols = []
        for item in _split_top(body):
            first = item.split()[0]
            if first.upper() not in CONSTRAINT_WORDS:
                cols.append(first.strip('"'))
        out[table] = cols
    return out


def migration_order(revisions: dict[str, str | None]) -> list[str]:
    children: dict[str | None, list[str]] = {}
    for rev, down in revisions.items():
        if down is not None and down not in revisions:
            raise ValueError(f"{rev}: нет ревизии {down}")
        children.setdefault(down, []).append(rev)
    order, cur = [], None
    while cur in children:
        nxt = children[cur]
        if len(nxt) > 1:
            raise ValueError(f"ветвление после {cur}: {sorted(nxt)}")
        cur = nxt[0]
        order.append(cur)
    if len(order) != len(revisions):
        raise ValueError("цикл или несвязанные ревизии")
    return order


def review_migration(text: str) -> list[str]:
    warnings = []
    up, _, down = text.partition("def downgrade")
    if re.search(r"op\.drop_(column|table)\(", up):
        warnings.append("drop")
    for call in re.findall(r"op\.add_column\((.*?)\)\s*$", up, re.M):
        if "nullable=False" in call and "server_default" not in call:
            warnings.append("not_null_without_default")
    if not re.search(r"op\.", down):
        warnings.append("empty_downgrade")
    return warnings
