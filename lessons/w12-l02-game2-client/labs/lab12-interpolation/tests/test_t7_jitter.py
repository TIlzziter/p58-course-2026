import pytest
from jitter import percentile, render_delay


def test_percentile_nearest_rank():
    assert percentile([5, 1, 3, 2, 4], 0.5) == 3
    assert percentile(list(range(1, 101)), 0.95) == 95
    assert percentile([7], 0.99) == 7
    with pytest.raises(ValueError):
        percentile([], 0.5)


def test_stable_network():
    arrivals = [i * 100 for i in range(20)]
    assert render_delay(arrivals, 100) == 100


def test_jittery_network():
    arrivals = [0, 100, 230, 300, 400, 520, 600, 700, 800, 900, 1000]
    # интервалы 100 130 70 100 120 80 100 100 100 100 → отклонения 0 30 30 0 20 20 0 0 0 0; p95 = 30
    assert render_delay(arrivals, 100) == 130


def test_few_samples_and_min():
    assert render_delay([0], 50) == 100
    assert render_delay([0, 50, 100], 50, min_delay=120) == 120
