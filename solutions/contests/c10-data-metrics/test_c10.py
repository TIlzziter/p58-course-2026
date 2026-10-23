import math

import pytest
from abtest import assign, report, srm_check
from heavy import heavy_hitters, misra_gries
from tasks import (
    ab_test,
    binom_p,
    dau_series,
    histogram,
    moving_average,
    percentile,
    pivot,
    ranks,
    retention_matrix,
    running_by_user,
    sessionize,
    simpson,
    to_local_day,
    welford,
)


def test_a1():
    assert percentile([50, 55, 60, 62, 2400], 90) == 1464.8
    assert percentile([50, 55, 60, 62, 65], 90) == 63.8
    assert percentile([10, 20, 30, 40], 50) == 25.0
    assert percentile([7], 99) == 7
    assert percentile([3, 1, 2], 0) == 1 and percentile([3, 1, 2], 100) == 3
    with pytest.raises(ValueError):
        percentile([], 50)
    with pytest.raises(ValueError):
        percentile([1], 101)


def test_a2():
    assert moving_average([3, 5, 4, 8, 10], 3) == [None, None, 4.0, 5.67, 7.33]
    assert moving_average([1, 2], 1) == [1.0, 2.0]
    assert moving_average([1, 2], 3) == [None, None]
    xs = [i % 7 for i in range(1000)]
    assert moving_average(xs, 5)[-1] == round(sum(xs[-5:]) / 5, 2)


def test_a3():
    assert histogram([0, 1, 2, 2.5, 5, 9.99, 10, 11, -1], 0, 10, 4) == [3, 1, 1, 2]
    assert histogram([], 0, 1, 3) == [0, 0, 0]
    assert histogram([1, 1, 1], 1, 2, 2) == [3, 0]


def test_a4():
    assert welford([2, 4, 4, 4, 5, 5, 7, 9]) == (8, 5.0, 2.1381)
    assert welford([]) == (0, 0.0, 0.0)
    assert welford([5]) == (1, 5.0, 0.0)
    assert welford(iter([1e9 + 4, 1e9 + 7, 1e9 + 13, 1e9 + 16])) == (4, 1e9 + 10, 5.4772)


def test_b1():
    assert to_local_day("2027-03-01T22:30:00Z", 3) == "2027-03-02"
    assert to_local_day("2027-03-01T02:00:00Z", -5) == "2027-02-28"
    assert to_local_day("2027-03-01T20:59:59Z", 3) == "2027-03-01"
    assert to_local_day("2027-12-31T21:00:00Z", 3) == "2028-01-01"


def test_b2():
    ev = [(1, "2027-03-01"), (2, "2027-03-01"), (1, "2027-03-01"), (1, "2027-03-02"), (3, "2027-03-04")]
    assert dau_series(ev, "2027-03-01", "2027-03-05") == [2, 1, 0, 1, 0]
    assert dau_series(ev, "2027-02-28", "2027-03-01") == [0, 2]
    assert dau_series([], "2027-03-01", "2027-03-01") == [0]


def test_b3():
    ev = [(1, "2027-03-01"), (2, "2027-03-01"), (1, "2027-03-02"), (2, "2027-03-03"),
          (3, "2027-03-02"), (3, "2027-03-03"), (1, "2027-03-03")]
    assert retention_matrix(ev, 2) == {"2027-03-01": [1.0, 0.5, 1.0], "2027-03-02": [1.0, 1.0, None]}
    assert retention_matrix([(5, "2027-03-01"), (6, "2027-03-01"), (7, "2027-03-01"),
                             (5, "2027-03-02")], 1) == {"2027-03-01": [1.0, 0.33]}


def test_c1():
    assert ranks([300, 250, 250, 100, 300, 90]) == ([1, 3, 3, 5, 1, 6], [1, 2, 2, 3, 1, 4])
    assert ranks([]) == ([], [])
    assert ranks([5, 5, 5]) == ([1, 1, 1], [1, 1, 1])


def test_c2():
    rows = [("ann", "03-02", 5), ("bob", "03-01", 2), ("ann", "03-01", 3), ("bob", "03-03", 4), ("ann", "03-03", 1)]
    assert running_by_user(rows) == [8, 2, 3, 6, 9]
    assert running_by_user([]) == []


def test_c3():
    rows = [("ann", "win", 2), ("bob", "loss", 1), ("ann", "loss", 3), ("ann", "win", 1), ("cat", "draw", 1)]
    assert pivot(rows) == (["draw", "loss", "win"],
                           [("ann", [0, 3, 3]), ("bob", [0, 1, 0]), ("cat", [1, 0, 0])])
    assert pivot([]) == ([], [])


def test_c4():
    ev = [(1, 100), (1, 0), (1, 250), (2, 10), (1, 1000), (1, 1100), (2, 5000)]
    assert sessionize(ev, 300) == {1: [(0, 250, 3), (1000, 1100, 2)], 2: [(10, 10, 1), (5000, 5000, 1)]}
    assert sessionize([(1, 0), (1, 300)], 300) == {1: [(0, 300, 2)]}
    assert sessionize([(1, 0), (1, 301)], 300) == {1: [(0, 0, 1), (301, 301, 1)]}
    assert sessionize([], 10) == {}


def test_d1():
    assert binom_p(9, 10) == 0.0215
    assert binom_p(2, 3) == 1.0 and binom_p(0, 0) == 1.0
    assert binom_p(620, 1053) == 0.0
    assert binom_p(540, 1000) == 0.0124
    with pytest.raises(ValueError):
        binom_p(5, 3)


def test_d2():
    assert ab_test(120, 1000, 150, 1000) == (1.963, 0.0496)
    assert ab_test(5, 50, 9, 50) == (1.1528, 0.249)
    assert ab_test(0, 10, 0, 10) == (0.0, 1.0)
    z, p = ab_test(150, 1000, 120, 1000)
    assert z == -1.963 and p == 0.0496


def test_d3():
    r = simpson({"новички": (81, 87, 234, 270), "опытные": (192, 263, 55, 80)})
    assert r == {"overall": "B", "by_group": {"новички": "A", "опытные": "A"}, "paradox": True}
    assert simpson({"x": (1, 2, 1, 2)}) == {"overall": "tie", "by_group": {"x": "tie"}, "paradox": False}
    assert simpson({"x": (3, 4, 1, 4), "y": (1, 4, 3, 4)})["paradox"] is False
    assert simpson({"x": (1, 3, 1, 3), "y": (2, 3, 1, 3)})["paradox"] is False


def test_e4a():
    got = [assign(u, "hint_v2", ["control", "test"], [50, 50]) for u in range(1, 9)]
    assert got == ["test", "control", "test", "test", "control", "test", "control", "control"]
    assert assign(42, "hint_v2", ["a", "b", "c"], [20, 30, 50]) == "c"
    assert all(assign(u, "x", ["only"], [100]) == "only" for u in range(20))
    share = sum(assign(u, "exp", ["a", "b"], [10, 90]) == "a" for u in range(10000)) / 10000
    assert 0.08 < share < 0.12
    with pytest.raises(ValueError):
        assign(1, "x", ["a", "b"], [50, 40])


def test_e4b():
    assert srm_check([5000, 5000], [50, 50]) == 1.0
    assert srm_check([5150, 4850], [50, 50]) == 0.0027
    assert srm_check([2100, 2900, 5000], [20, 30, 50]) == 0.0155


def _is_test(u):
    return assign(u, "hint_v2", ["control", "test"], [50, 50]) == "test"


def test_e4c():
    users = list(range(1, 2001))
    r = report(users, {u for u in users if u % 5 == 0 or (_is_test(u) and u % 10 == 3)}, "hint_v2")
    assert r == {"n": {"control": 982, "test": 1018}, "conv": {"control": 204, "test": 291}, "srm_p": 0.4208,
                 "z": 4.0468, "p": 0.0001, "lift": 0.0781, "decision": "ship"}
    r = report(users, {u for u in users if u % 5 == 0 or (not _is_test(u) and u % 10 == 3)}, "hint_v2")
    assert r["decision"] == "rollback" and r["lift"] < 0
    assert report(users, {u for u in users if u % 5 == 0}, "hint_v2")["decision"] == "wait"
    skew = [u for u in range(1, 3001) if _is_test(u) or u % 3 == 0]
    assert report(skew, set(), "hint_v2")["decision"] == "broken"


def test_e5():
    s = "abracadabraalakazam"
    assert misra_gries(s, 3) == {"a": 4}
    assert heavy_hitters(s, 3) == ["a"]
    assert misra_gries("aabbc", 3) == {"a": 1, "b": 1}
    stream = [1] * 40 + [2] * 30 + list(range(100, 130))
    assert heavy_hitters(stream, 4) == [1, 2]
    assert len(misra_gries(range(1000), 10)) <= 9
    assert math.isclose(sum(misra_gries([7] * 10, 2).values()), 10)
