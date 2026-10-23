"""Индексы и EXPLAIN на SQLite (задача 6). В PostgreSQL идея та же, вывод EXPLAIN другой."""
import random
import sqlite3

SCHEMA = """
CREATE TABLE matches (
    id INTEGER PRIMARY KEY,
    room TEXT NOT NULL,
    player_id INTEGER NOT NULL,
    score INTEGER NOT NULL,
    finished_at TEXT NOT NULL
);
"""

QUERIES = {
    "history": "SELECT id, score FROM matches WHERE player_id = ? ORDER BY finished_at DESC LIMIT 20",
    "room_top": "SELECT player_id, MAX(score) FROM matches WHERE room = ? GROUP BY player_id",
    "recent": "SELECT COUNT(*) FROM matches WHERE finished_at >= ?",
}


def make_db(n: int = 20000, seed: int = 58) -> sqlite3.Connection:
    rng = random.Random(seed)
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA)
    rows = [(rng.choice(["snake", "chess", "quiz", "c4"]), rng.randint(1, 500), rng.randint(0, 1000),
             f"2027-04-{rng.randint(1, 30):02d}T{rng.randint(0, 23):02d}:00:00") for _ in range(n)]
    conn.executemany("INSERT INTO matches (room, player_id, score, finished_at) VALUES (?, ?, ?, ?)", rows)
    return conn


def plan(conn: sqlite3.Connection, sql: str, params=()) -> str:
    """Текст EXPLAIN QUERY PLAN одной строкой: детали шагов через "; "."""
    return "; ".join(row[3] for row in conn.execute("EXPLAIN QUERY PLAN " + sql, params))


def uses_full_scan(conn, sql, params=()) -> bool:
    """True, если в плане есть полный просмотр таблицы matches: шаг "SCAN matches" без "USING"."""
    return any(step.startswith("SCAN matches") and "USING" not in step for step in plan(conn, sql, params).split("; "))


def add_indexes(conn: sqlite3.Connection) -> list[str]:
    """Создать индексы так, чтобы ни один запрос из QUERIES не просматривал таблицу целиком, а history ещё
    и не сортировал отдельно (в плане нет "USE TEMP B-TREE FOR ORDER BY"). Не больше трёх индексов.
    Ответ — список созданных имён."""
    ddl = {
        "ix_matches_player_finished": "CREATE INDEX ix_matches_player_finished ON matches (player_id, finished_at)",
        "ix_matches_room_player": "CREATE INDEX ix_matches_room_player ON matches (room, player_id, score)",
        "ix_matches_finished": "CREATE INDEX ix_matches_finished ON matches (finished_at)",
    }
    for sql in ddl.values():
        conn.execute(sql)
    return list(ddl)
