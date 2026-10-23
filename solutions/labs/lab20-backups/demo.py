"""Учебная база игры (SQLite вместо PostgreSQL — чтобы лаба работала без сервера)."""
import random
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT NOT NULL, rating INTEGER NOT NULL);
CREATE TABLE matches (id INTEGER PRIMARY KEY, player_id INTEGER NOT NULL REFERENCES players(id),
                      score INTEGER NOT NULL, finished_at TEXT NOT NULL);
"""


def make_demo_db(path: str | Path, players: int = 50, matches: int = 500, seed: int = 58) -> Path:
    path = Path(path)
    path.unlink(missing_ok=True)
    rng = random.Random(seed)
    con = sqlite3.connect(path)
    con.executescript(SCHEMA)
    con.executemany("INSERT INTO players VALUES (?, ?, ?)",
                    [(i, f"player{i}", rng.randint(800, 2000)) for i in range(1, players + 1)])
    con.executemany("INSERT INTO matches VALUES (?, ?, ?, ?)",
                    [(i, rng.randint(1, players), rng.randint(0, 100), f"2027-04-{rng.randint(1, 28):02d}")
                     for i in range(1, matches + 1)])
    con.commit()
    con.close()
    return path


def table_counts(path: str | Path) -> dict[str, int]:
    con = sqlite3.connect(path)
    try:
        names = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name")]
        return {n: con.execute(f'SELECT COUNT(*) FROM "{n}"').fetchone()[0] for n in names}
    finally:
        con.close()
