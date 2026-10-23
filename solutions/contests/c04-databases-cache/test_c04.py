import sqlite3
from itertools import combinations

import fakeredis
import pytest

from lru import LRU
from tasks import (SCHEMA, add_win, best_streak, elo_delta, games_count, migration_order, once, parse_ddl,
                   rank_with_ties, remember_recent, replay, review_migration, sliding_allow, top_players,
                   top_wins, win_rate)
from tournament import round_robin, standings, swiss_pairs


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    c.executescript(SCHEMA)
    c.executemany("INSERT INTO players (name, rating) VALUES (?, ?)",
                  [("Аня", 1100), ("Боря", 1050), ("Вика", 1100), ("Гоша", 1000)])
    c.executemany("INSERT INTO matches (p1, p2, result) VALUES (?, ?, ?)",
                  [(1, 2, "win1"), (2, 3, "draw"), (3, 1, "win2"), (1, 2, "win2"), (1, 3, "win1"), (1, 2, "win1")])
    return c


@pytest.fixture
async def r():
    client = fakeredis.FakeAsyncRedis(server=fakeredis.FakeServer(), decode_responses=True)
    yield client
    await client.aclose()


def test_a1(conn):
    assert top_players(conn, 3) == [("Аня", 1100), ("Вика", 1100), ("Боря", 1050)]
    assert top_players(conn, 10)[-1] == ("Гоша", 1000)


def test_a2(conn):
    assert games_count(conn) == {"Аня": 5, "Боря": 4, "Вика": 3, "Гоша": 0}


def test_a3(conn):
    assert win_rate(conn, "Аня") == 0.8
    assert win_rate(conn, "Боря") == 0.25
    assert win_rate(conn, "Гоша") is None
    assert win_rate(conn, "Нет такого") is None


def test_a4(conn):
    assert best_streak(conn, "Аня") == 2
    assert best_streak(conn, "Вика") == 0
    conn.executemany("INSERT INTO matches (p1, p2, result) VALUES (?, ?, ?)", [(4, 1, "win1")] * 3)
    assert best_streak(conn, "Гоша") == 3


def test_b1():
    assert elo_delta(1000, 1000, 1) == 16
    assert elo_delta(1200, 1000, 1) == 8
    assert elo_delta(1000, 1200, 1) == 24
    assert elo_delta(1200, 1000, 0.5) == -8
    assert elo_delta(1000, 1000, 1, k=10) == 5


def test_b2():
    assert replay([("Аня", "Боря", "win1"), ("Боря", "Вика", "draw"), ("Аня", "Вика", "win2")]) == \
        {"Аня": 999, "Боря": 985, "Вика": 1016}
    assert replay([]) == {}
    assert replay([("a", "b", "draw")], start=1500) == {"a": 1500, "b": 1500}


def test_b3():
    assert rank_with_ties({"Аня": 1100, "Боря": 1050, "Вика": 1100, "Гоша": 1000}) == \
        [(1, "Аня"), (1, "Вика"), (3, "Боря"), (4, "Гоша")]
    assert rank_with_ties({}) == []


async def test_c1(r):
    for name in ["Аня", "Боря", "Аня", "Вика", "Боря", "Аня"]:
        await add_win(r, name)
    assert await add_win(r, "Гоша") == 1
    assert await top_wins(r, 3) == [("Аня", 3), ("Боря", 2), ("Вика", 1)]


async def test_c2(r):
    for g in ["c4", "snake", "c4", "chess", "go", "ttt", "mines"]:
        items = await remember_recent(r, "u1", g)
    assert items == ["mines", "ttt", "go", "chess", "c4"]
    assert await remember_recent(r, "u1", "go", limit=3) == ["go", "mines", "ttt"]


async def test_c3(r):
    assert await once(r, "match:42", 60) is True
    assert await once(r, "match:42", 60) is False
    assert await once(r, "match:43", 60) is True
    assert 1 <= await r.ttl("once:match:42") <= 60


async def test_c4(r):
    res = [await sliding_allow(r, "u", 3, 10, t) for t in [0, 1, 2, 3, 9.5, 10.5, 11, 12, 13]]
    assert res == [True, True, True, False, False, True, True, True, False]


DDL = """
CREATE TABLE players (
    id INTEGER PRIMARY KEY,
    tg_id BIGINT NOT NULL,
    name VARCHAR(64),
    rating NUMERIC(6, 1) DEFAULT 1000,
    UNIQUE (tg_id)
);
create table if not exists matches (id integer primary key, p1 int, p2 int,
    foreign key (p1) references players(id), check (p1 <> p2));
"""


def test_d1():
    assert parse_ddl(DDL) == {"players": ["id", "tg_id", "name", "rating"], "matches": ["id", "p1", "p2"]}


def test_d2():
    assert migration_order({"c3": "b2", "a1": None, "b2": "a1"}) == ["a1", "b2", "c3"]
    assert migration_order({}) == []
    for bad in [{"a": None, "b": "a", "c": "a"}, {"a": None, "b": "x"}, {"a": "b", "b": "a"}, {"a": None, "b": None}]:
        with pytest.raises(ValueError):
            migration_order(bad)


MIG_OK = '''
def upgrade() -> None:
    op.add_column("players", sa.Column("avatar", sa.String(200), nullable=True))
    op.add_column("players", sa.Column("level", sa.Integer(), nullable=False, server_default="1"))


def downgrade() -> None:
    op.drop_column("players", "level")
    op.drop_column("players", "avatar")
'''
MIG_BAD = '''
def upgrade() -> None:
    op.drop_column("players", "rating")
    op.add_column("players", sa.Column("elo", sa.Integer(), nullable=False))


def downgrade() -> None:
    pass
'''


def test_d3():
    assert review_migration(MIG_OK) == []
    assert review_migration(MIG_BAD) == ["drop", "not_null_without_default", "empty_downgrade"]


@pytest.mark.parametrize("n", [2, 3, 4, 5, 6, 7, 8])
def test_e4a(n):
    players = [f"p{i}" for i in range(n)]
    rounds = round_robin(players)
    assert len(rounds) == (n - 1 if n % 2 == 0 else n)
    met = []
    for rnd in rounds:
        flat = [x for pair in rnd for x in pair if x is not None]
        assert len(flat) == len(set(flat)) == n          # каждый ровно один раз (с None — отдыхает)
        met += [frozenset(p) for p in rnd if None not in p]
    assert sorted(met, key=sorted) == sorted((frozenset(c) for c in combinations(players, 2)), key=sorted)
    assert round_robin(["A", "B", "C", "D"])[0] == [("A", "D"), ("B", "C")]


def test_e4b():
    res = [("Аня", "Боря", "win1"), ("Боря", "Вика", "draw"), ("Вика", "Аня", "win1")]
    assert standings(["Аня", "Боря", "Вика", "Гоша"], res) == [
        ("Вика", 4, 1, 1, 0), ("Аня", 3, 1, 0, 1), ("Боря", 1, 0, 1, 1), ("Гоша", 0, 0, 0, 0)]
    assert standings(["a", "b"], [("a", "b", "draw"), ("a", "b", "draw"), ("b", "a", "win1")])[0] == ("b", 5, 1, 2, 0)
    with pytest.raises(ValueError):
        standings(["a", "b"], [("a", "x", "win1")])


def test_e4c():
    assert swiss_pairs(["A", "B", "C", "D"], set()) == [("A", "B"), ("C", "D")]
    assert swiss_pairs(["A", "B", "C", "D"], {frozenset("AB")}) == [("A", "C"), ("B", "D")]
    assert swiss_pairs(["A", "B", "C", "D"], {frozenset("AB"), frozenset("AC")}) == [("A", "D"), ("B", "C")]
    # жадно A–B, C–D нельзя (C и D уже играли) → нужен возврат
    assert swiss_pairs(list("ABCD"), {frozenset("CD")}) == [("A", "C"), ("B", "D")]
    with pytest.raises(ValueError):
        swiss_pairs(list("ABCD"), {frozenset(p) for p in combinations("ABCD", 2)})
    with pytest.raises(ValueError):
        swiss_pairs(list("ABC"), set())


def test_e5():
    c = LRU(2)
    c.put("a", 1)
    c.put("b", 2)
    assert c.get("a") == 1           # a стал свежим
    c.put("c", 3)                    # вытесняем b
    assert c.get("b") is None and c.get("b", "нет") == "нет"
    assert c.keys() == ["a", "c"] and len(c) == 2
    c.put("a", 10)
    c.put("d", 4)                    # вытесняем c
    assert c.keys() == ["a", "d"] and c.get("a") == 10
    assert (c.hits, c.misses) == (2, 2)
    with pytest.raises(ValueError):
        LRU(0)
