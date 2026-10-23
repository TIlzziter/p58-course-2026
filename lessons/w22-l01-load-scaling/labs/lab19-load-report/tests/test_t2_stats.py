import pytest
from loadlog import endpoint_stats, load_log, percentile


def test_percentile_nearest_rank():
    xs = [15, 20, 35, 40, 50]
    assert percentile(xs, 30) == 20 and percentile(xs, 40) == 20 and percentile(xs, 50) == 35
    assert percentile(xs, 100) == 50 and percentile(xs, 0) == 15
    assert percentile(list(range(1, 101)), 95) == 95 and percentile(list(range(1, 101)), 99) == 99
    with pytest.raises(ValueError):
        percentile([], 50)


def test_small_stats(small_csv):
    reqs, _ = load_log(small_csv)
    st = endpoint_stats(reqs)
    assert list(st) == ["GET /a", "GET /b"]
    a = st["GET /a"]
    assert a["count"] == 4 and a["failures"] == 1 and a["fail_rate"] == 0.25
    assert a["rps"] == round(4 / 3.5, 2)
    assert (a["p50"], a["p95"], a["p99"], a["max"]) == (20.0, 40.0, 40.0, 40.0)
    b = st["GET /b"]
    assert b["failures"] == 1 and b["p50"] == 50.0 and b["max"] == 100.0


def test_empty():
    assert endpoint_stats([]) == {}


def test_real_before(before_path):
    st = endpoint_stats(load_log(before_path)[0])
    lb = st["GET /api/leaderboard"]
    assert lb["count"] == 904 and lb["failures"] == 16 and lb["fail_rate"] == 0.0177
    assert lb["p50"] == 424.1 and lb["p95"] == 874.9 and lb["p99"] == 1922.4
    assert st["GET /api/rooms"]["rps"] == 35.32
    assert sum(s["count"] for s in st.values()) == 6000
