from alerts import evaluate


def test_short_spike_ignored():
    s = [(0, 1), (15, 9), (30, 1), (45, 1)]
    assert evaluate(s, threshold=5, for_s=30) == []


def test_fires_after_for_and_resolves():
    s = [(0, 1), (15, 9), (30, 9), (45, 9), (60, 2), (75, 1)]
    assert evaluate(s, 5, 30) == [(45, "firing"), (60, "resolved")]


def test_equal_threshold_is_ok():
    assert evaluate([(0, 5), (60, 5)], 5, 0) == []


def test_zero_for_and_flapping():
    s = [(0, 9), (10, 1), (20, 9), (30, 9), (40, 1)]
    assert evaluate(s, 5, 0) == [(0, "firing"), (10, "resolved"), (20, "firing"), (40, "resolved")]


def test_pending_reset_by_dip():
    s = [(0, 9), (20, 9), (25, 1), (30, 9), (50, 9), (60, 9)]
    assert evaluate(s, 5, 30) == [(60, "firing")]
