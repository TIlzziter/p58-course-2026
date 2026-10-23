import pytest
from evals import ab_compare


def test_counts_and_p():
    a = {f"c{i}": True for i in range(10)}
    b = dict(a)
    for i in range(8):
        b[f"c{i}"] = False                   # A выигрывает 8 раз, B — 0
    r = ab_compare(a, b)
    assert r == {"wins_a": 8, "wins_b": 0, "ties": 2, "p_value": 0.0078}


def test_not_significant():
    a = {"1": True, "2": True, "3": False, "4": True, "5": False}
    b = {"1": False, "2": False, "3": True, "4": True, "5": False}
    assert ab_compare(a, b) == {"wins_a": 2, "wins_b": 1, "ties": 2, "p_value": 1.0}


def test_symmetric_and_edge():
    a = {str(i): i < 15 for i in range(20)}
    b = {str(i): i >= 15 for i in range(20)}
    r1, r2 = ab_compare(a, b), ab_compare(b, a)
    assert r1["p_value"] == r2["p_value"] == 0.0414
    assert ab_compare({"x": True}, {"x": True})["p_value"] == 1.0
    with pytest.raises(ValueError):
        ab_compare({"x": True}, {"y": True})
