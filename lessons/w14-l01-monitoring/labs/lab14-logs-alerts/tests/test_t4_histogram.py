import pytest
from metrics import Histogram


def make():
    h = Histogram("ws_tick_seconds", [0.01, 0.05, 0.1, 0.5])
    for v in [0.004, 0.02, 0.03, 0.04, 0.07, 0.2, 0.9, 0.05]:
        h.observe(v)
    return h


def test_render():
    assert make().render() == (
        'ws_tick_seconds_bucket{le="0.01"} 1\n'
        'ws_tick_seconds_bucket{le="0.05"} 5\n'          # 0.05 попадает в le="0.05": граница включается
        'ws_tick_seconds_bucket{le="0.1"} 6\n'
        'ws_tick_seconds_bucket{le="0.5"} 7\n'
        'ws_tick_seconds_bucket{le="+Inf"} 8\n'
        'ws_tick_seconds_sum 1.314\n'
        'ws_tick_seconds_count 8\n'
    )


def test_empty_render():
    assert Histogram("x", [1]).render() == 'x_bucket{le="1"} 0\nx_bucket{le="+Inf"} 0\nx_sum 0\nx_count 0\n'


def test_bad_buckets():
    for b in ([], [0.5, 0.1], [1, 1]):
        with pytest.raises(ValueError):
            Histogram("x", b)


def test_quantile():
    h = make()
    assert h.quantile(0.5) == pytest.approx(0.01 + 0.04 * 3 / 4)       # ранг 4 из 8 — внутри (0.01, 0.05]
    assert h.quantile(0.125) == pytest.approx(0.01)
    assert h.quantile(0.75) == pytest.approx(0.1)
    assert h.quantile(0.99) == pytest.approx(0.5)                       # в +Inf — верхняя конечная граница
    assert Histogram("x", [1]).quantile(0.5) is None
