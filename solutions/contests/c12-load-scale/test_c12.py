import asyncio
import math
from collections import Counter

import pytest
from autoscale import desired, simulate, stabilize
from breaker import CircuitBreaker, run
from tasks import (
    Ring,
    SingleFlight,
    apdex,
    error_budget,
    hist_percentile,
    lru_hits,
    max_replicas,
    mm1,
    moved_mod,
    n_plus_one,
    pick_index,
    pool_size,
    queue_waits,
    rps_series,
    token_bucket,
)

H = [(10, 50), (25, 30), (50, 15), (100, 4), (250, 1)]
IX = {
    "ix_player": ("player_id",),
    "ix_player_time": ("player_id", "finished_at"),
    "ix_room_player": ("room", "player_id"),
    "ix_time": ("finished_at",),
}


def test_a1():
    assert rps_series([0.1, 0.5, 1.2, 3.9, 3.0]) == [2, 1, 0, 2]
    assert rps_series([]) == []
    assert rps_series([0.0]) == [1]


def test_a2():
    assert apdex([100, 200, 300, 500, 900, 1200, 2500], 300) == 0.64
    assert apdex([50] * 9 + [5000], 100) == 0.9
    assert apdex([400], 100) == 0.5
    with pytest.raises(ValueError):
        apdex([], 100)


def test_a3():
    assert error_budget(30, 100_000) == {"allowed": 100, "burn": 0.3, "left": 70}
    assert error_budget(5, 1000) == {"allowed": 1, "burn": 5.0, "left": 0}
    assert error_budget(0, 10) == {"allowed": 0, "burn": 0.0, "left": 0}
    assert error_budget(2, 500)["burn"] == math.inf
    assert error_budget(10, 1000, slo=0.99)["burn"] == 1.0


def test_a4():
    assert hist_percentile(H, 50) == 10
    assert hist_percentile(H, 95) == 50
    assert hist_percentile(H, 99.5) == 250
    assert hist_percentile(H, 80) == 25
    with pytest.raises(ValueError):
        hist_percentile([(10, 0)], 50)


def test_b1():
    assert mm1(80, 100) == {"rho": 0.8, "L": 4.0, "W_ms": 50.0}
    assert mm1(50, 100) == {"rho": 0.5, "L": 1.0, "W_ms": 20.0}
    assert mm1(95, 100)["W_ms"] == 200.0
    with pytest.raises(ValueError):
        mm1(100, 100)


def test_b2():
    assert queue_waits([0, 1, 2, 3, 4], [3] * 5, 1) == [0, 2, 4, 6, 8]
    assert queue_waits([0, 0, 0, 1], [2] * 4, 2) == [0, 0, 2, 1]
    assert queue_waits([0, 1, 2, 3, 4], [3] * 5, 3) == [0] * 5


def test_b3():
    t = [0, 0, 0, 0, 0.5, 1, 1, 3, 3, 3, 3]
    assert token_bucket(1, 3, t) == [True] * 3 + [False] * 2 + [True, False, True, True, False, False]
    assert token_bucket(10, 1, [0, 0.05, 0.1, 0.2]) == [True, False, True, True]
    assert all(token_bucket(100, 5, [i * 0.01 for i in range(50)]))


def test_c1():
    ks = list(range(10_000))
    assert moved_mod(ks, 4, 5) == 0.8
    assert moved_mod(ks, 4, 8) == 0.5
    assert moved_mod(ks, 3, 3) == 0.0


def test_c2():
    r = Ring(["api1", "api2", "api3"])
    r2 = Ring(["api1", "api2", "api3", "api4"])
    assert r.node("room:7") == "api2" and r.node("room:42") == "api3"
    keys = [f"room:{i}" for i in range(2000)]
    moved = [k for k in keys if r.node(k) != r2.node(k)]
    assert all(r2.node(k) == "api4" for k in moved)
    assert len(moved) == 494
    assert Counter(r.node(k) for k in keys) == {"api1": 751, "api2": 687, "api3": 562}
    assert Ring(["solo"], vnodes=1).node("x") == "solo"


def test_c3():
    assert lru_hits(2, list("abacbdab")) == (1, ["a", "b"])
    assert lru_hits(3, list("abacbdab")) == (3, ["d", "a", "b"])
    assert lru_hits(1, list("aaab")) == (2, ["b"])


def test_c4():
    async def main():
        calls = []

        async def fetch(k):
            calls.append(k)
            await asyncio.sleep(0.01)
            if k == "bad":
                raise RuntimeError(k)
            return k.upper()

        sf = SingleFlight(fetch)
        res = await asyncio.gather(*(sf.get("lb") for _ in range(10)), sf.get("x"))
        assert res == ["LB"] * 10 + ["X"] and calls == ["lb", "x"]
        assert await sf.get("lb") == "LB" and calls.count("lb") == 2
        bad = await asyncio.gather(*(sf.get("bad") for _ in range(3)), return_exceptions=True)
        assert all(isinstance(e, RuntimeError) for e in bad) and calls.count("bad") == 1

    asyncio.run(main())


def test_d1():
    qs = ["SELECT * FROM rooms WHERE owner = 7"]
    qs += [f"SELECT name FROM users WHERE id = {i}" for i in (3, 5, 9, 12)]
    qs += ["SELECT * FROM rooms WHERE  owner = 8", "SELECT 1"]
    assert n_plus_one(qs, 2) == [
        ("SELECT name FROM users WHERE id = ?", 4),
        ("SELECT * FROM rooms WHERE owner = ?", 2),
    ]
    assert n_plus_one(qs) == [("SELECT name FROM users WHERE id = ?", 4)]
    s = [f"SELECT * FROM u WHERE name = '{n}'" for n in ("ann", "o''neil", "bob")]
    assert n_plus_one(s) == [("SELECT * FROM u WHERE name = ?", 3)]


def test_d2():
    assert pool_size(200, 2, 15) == 9
    assert pool_size(50, 1, 10) == 1
    assert pool_size(70, 1, 10) == 1
    assert max_replicas(100, 9) == 10
    assert max_replicas(100, 20, reserved=5) == 4


def test_d3():
    assert pick_index({"player_id"}, "finished_at", IX) == "ix_player_time"
    assert pick_index({"player_id"}, None, IX) == "ix_player"
    assert pick_index({"room", "player_id"}, None, IX) == "ix_room_player"
    assert pick_index({"score"}, None, IX) is None
    assert pick_index({"finished_at"}, None, IX) == "ix_time"
    assert pick_index({"player_id", "finished_at"}, None, IX) == "ix_player_time"


def test_e4a():
    assert desired(3, 0.9, 0.6) == 5
    assert desired(3, 0.65, 0.6) == 3
    assert desired(4, 0.1, 0.6) == 1
    assert desired(2, 3.0, 0.6) == 10
    assert desired(2, 0.3, 0.6, lo=2) == 2


def test_e4b():
    assert stabilize([2, 5, 3, 3, 1, 1, 1], 3) == [2, 5, 5, 5, 3, 3, 1]
    assert stabilize([4, 1, 2], 1) == [4, 1, 2]


def test_e4c():
    load = [50, 300, 300, 300, 100, 50, 50, 50]
    assert simulate(load, 100) == {"replicas": [1, 1, 5, 5, 5, 5, 5, 2], "dropped": 200.0, "peak": 5}
    assert simulate(load, 100, window=1)["replicas"] == [1, 1, 5, 5, 5, 2, 1, 1]
    assert simulate([1000] * 3, 50, hi=4)["dropped"] == 950 + 800 + 800


def test_e5():
    ev = [(0, False), (1, False), (2, False), (3, True), (5, True), (12, False), (13, True), (22, True), (23, True)]
    assert run(ev) == "xxx--x-++"
    assert run([(0, False), (1, True), (2, False), (3, False)]) == "x+xx"
    cb = CircuitBreaker(1, 5)
    cb.record(False, 0)
    assert cb.allow(5) and not cb.allow(5.1)
    cb.record(True, 6)
    assert cb.state == "closed" and cb.allow(6.5)
