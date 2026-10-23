import pytest
from metrics import percentile, red


def recs():
    out = []
    for i in range(20):
        out.append({"ts": 100 + i * 0.5, "status": 500 if i in (3, 7) else 200, "ms": 10 + i})
    return out


def test_percentile():
    assert percentile([5, 1, 4, 2, 3], 0.5) == 3 and percentile(list(range(1, 21)), 0.95) == 19


def test_red_window():
    r = red(recs(), 100, 110)
    assert r == {"rate": 2.0, "errors": 0.1, "p50": 19, "p95": 28}


def test_red_half_open():
    r = red(recs(), 100, 101)                  # ts 100, 100.5 — 101 уже не входит
    assert r["rate"] == 2.0 and r["p50"] == 10 and r["errors"] == 0


def test_red_empty():
    assert red(recs(), 0, 10) is None
    assert red([], 0, 1) is None


def test_red_errors_only_5xx():
    rs = [{"ts": 0, "status": s, "ms": 1} for s in (200, 404, 429, 500, 503)]
    assert red(rs, 0, 1)["errors"] == pytest.approx(0.4)
