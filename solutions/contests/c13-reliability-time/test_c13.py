from datetime import datetime

import pytest
from jobs import apply_rewards, next_attempt_at, simulate, timeline
from lease import Lease, run
from tasks import (
    Conflict,
    IdempotencyStore,
    availability,
    backoff_schedule,
    cron_next,
    downtime_budget,
    health_transitions,
    incident_stats,
    lamport,
    local_day_bounds,
    lww_merge,
    parse_duration,
    retry,
    uptime,
    utc_to_local,
    vc_compare,
)


def test_a1():
    assert [parse_duration(s) for s in ("1h30m", "2d", "1h 5m", "45s")] == [5400, 172800, 3900, 45]
    for bad in ("", "5x", "30m1h", "1.5h", "h"):
        with pytest.raises(ValueError):
            parse_duration(bad)


def test_a2():
    assert utc_to_local("2027-03-28T00:30:00Z", "Europe/Berlin") == "2027-03-28T01:30:00+01:00"
    assert utc_to_local("2027-03-28T01:30:00Z", "Europe/Berlin") == "2027-03-28T03:30:00+02:00"
    assert utc_to_local("2027-04-26T21:30:00Z", "Europe/Moscow") == "2027-04-27T00:30:00+03:00"
    assert local_day_bounds("2027-04-26", "Europe/Moscow") == ("2027-04-25T21:00:00Z", "2027-04-26T21:00:00Z")
    assert local_day_bounds("2027-03-28", "Europe/Berlin") == ("2027-03-27T23:00:00Z", "2027-03-28T22:00:00Z")


def test_a3():
    assert uptime([(100, 200), (150, 300), (900, 1100)], 0, 1000) == 70.0
    assert uptime([], 0, 10) == 100.0
    assert uptime([(-50, 10), (5, 6)], 0, 1000) == 99.0


def test_a4():
    assert cron_next("0 3 * * *", datetime(2027, 4, 26, 3, 0)) == datetime(2027, 4, 27, 3, 0)
    assert cron_next("*/15 9-18 * * 1-5", datetime(2027, 4, 30, 18, 50)) == datetime(2027, 5, 3, 9, 0)
    assert cron_next("30 12 * * 0,6", datetime(2027, 4, 26, 10)) == datetime(2027, 5, 1, 12, 30)
    assert cron_next("*/15 * * * *", datetime(2027, 4, 26, 10, 14, 59)) == datetime(2027, 4, 26, 10, 15)
    with pytest.raises(ValueError):
        cron_next("0 3 1 * *", datetime(2027, 1, 1))


def test_b1():
    assert backoff_schedule(6, 0.5, 5) == [0.5, 1.0, 2.0, 4.0, 5.0, 5.0]
    j = backoff_schedule(4, 1, 10, seed=58)
    assert j == [0.581, 0.411, 2.568, 7.572]
    assert all(0 <= x <= d for x, d in zip(j, backoff_schedule(4, 1, 10)))


def test_b2():
    calls, sl = [], []

    def flaky():
        calls.append(1)
        if len(calls) < 3:
            raise ConnectionError
        return "ok"

    assert retry(flaky, 5, (ConnectionError,), sleep=sl.append) == ("ok", 3) and sl == [0.1, 0.2]

    def bad():
        raise KeyError

    sl.clear()
    with pytest.raises(KeyError):
        retry(bad, 5, (ConnectionError,), sleep=sl.append)
    assert sl == []

    def down():
        raise TimeoutError

    with pytest.raises(TimeoutError):
        retry(down, 3, (TimeoutError,), sleep=sl.append)
    assert sl == [0.1, 0.2]


def test_b3():
    s, n = IdempotencyStore(ttl=100), []

    def fn(b):
        n.append(b)
        return {"order": len(n)}

    assert s.handle("k1", {"x": 1}, fn) == {"order": 1}
    assert s.handle("k1", {"x": 1}, fn, now=50) == {"order": 1} and len(n) == 1
    with pytest.raises(Conflict):
        s.handle("k1", {"x": 2}, fn, now=60)
    assert s.handle("k1", {"x": 2}, fn, now=100) == {"order": 2}

    def boom(b):
        raise RuntimeError

    with pytest.raises(RuntimeError):
        s.handle("k2", 1, boom)
    assert s.handle("k2", 1, fn) == {"order": 3}


def test_c1():
    assert availability(("series", [0.999, ("parallel", [0.99, 0.99]), 0.9995])) == 0.998401
    assert availability(("parallel", [0.9, 0.9, 0.9])) == 0.999
    assert availability(0.95) == 0.95


def test_c2():
    assert downtime_budget(99.9) == 43.2
    assert downtime_budget(99.5) == 216.0
    assert downtime_budget(99.99, 365) == 52.6


def test_c3():
    r = incident_stats([(3600, 4200), (4000, 4800), (86400, 87000)], 0, 7 * 86400)
    assert r == {"count": 2, "mttr_min": 15.0, "mtbf_h": 83.8}
    assert incident_stats([], 0, 100) == {"count": 0, "mttr_min": 0.0, "mtbf_h": None}


def test_c4():
    c = [True, False, False, True, False, False, False, False, True, False, True, True, True]
    assert health_transitions(c) == [(6, "down"), (11, "up")]
    assert health_transitions([False] * 2 + [True] * 5) == []
    assert health_transitions([False, True, False], fail_after=1, recover_after=1) == [
        (0, "down"), (1, "up"), (2, "down")]


def test_d1():
    ev = [("A", "local"), ("A", "send", "m1"), ("B", "local"), ("B", "local"), ("B", "local"),
          ("B", "recv", "m1"), ("B", "send", "m2"), ("A", "recv", "m2")]
    assert lamport(ev) == [1, 2, 1, 2, 3, 4, 5, 6]
    assert lamport([("A", "send", "x"), ("B", "recv", "x")]) == [1, 2]


def test_d2():
    assert vc_compare({"A": 1, "B": 2}, {"A": 1, "B": 3}) == "before"
    assert vc_compare({"A": 2}, {"B": 1}) == "concurrent"
    assert vc_compare({"A": 1}, {"A": 1, "B": 0}) == "equal"
    assert vc_compare({"A": 3, "B": 1}, {"A": 2}) == "after"


def test_d3():
    r1 = {"skin": (5, "api1", "red"), "lang": (1, "api1", "ru")}
    r2 = {"skin": (5, "api2", "blue"), "sound": (2, "api2", "off")}
    assert lww_merge(r1, r2) == {"lang": "ru", "skin": "blue", "sound": "off"}
    assert list(lww_merge(r1, r2)) == ["lang", "skin", "sound"]
    assert lww_merge(r2, r1) == lww_merge(r1, r2)
    assert lww_merge({"a": (9, "x", 1)}, {"a": (3, "z", 2)}) == {"a": 1}


J = {"a": (0, [False, False, True]), "b": (1, [True]), "c": (2, [])}


def test_e4a():
    assert next_attempt_at(10, 1) == 11.0 and next_attempt_at(10, 4) == 18.0
    assert next_attempt_at(10, 10, cap=60) == 70


def test_e4b():
    assert simulate(J) == {"a": ("done", 3, 3.0), "b": ("done", 1, 1), "c": ("dead", 4, 9.0)}
    assert timeline(J) == [(0, "a", 1), (1.0, "a", 2), (1, "b", 1), (2, "c", 1), (3.0, "a", 3),
                           (3.0, "c", 2), (5.0, "c", 3), (9.0, "c", 4)]
    assert simulate(J, max_attempts=2)["a"] == ("dead", 2, 1.0)


def test_e4c():
    d = [("e1", "ann", 10), ("e2", "bob", 5), ("e1", "ann", 10), ("e3", "ann", 3)]
    assert apply_rewards(d) == {"ann": 13, "bob": 5}
    with pytest.raises(ValueError):
        apply_rewards([("e1", "ann", 10), ("e1", "ann", 99)])


def test_e5():
    sc = [("acq", "A", 0), ("write", 1, "a1"), ("acq", "B", 5), ("acq", "B", 12), ("write", 2, "b1"),
          ("write", 1, "a2"), ("acq", "A", 13), ("rel", "B", 2), ("acq", "A", 14), ("write", 3, "a3")]
    assert run(sc) == [1, True, None, 2, True, False, None, True, 3, True]
    lease = Lease(10)
    assert lease.acquire("A", 0) == 1 and lease.acquire("A", 9) == 1 and lease.acquire("B", 18) is None
    assert lease.acquire("B", 19) == 2 and not lease.release("A", 1)
