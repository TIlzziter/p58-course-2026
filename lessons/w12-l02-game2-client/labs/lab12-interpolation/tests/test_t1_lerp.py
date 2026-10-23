import pytest
from interp import clamp, ease_out_quad, lerp, lerp_point


def test_lerp():
    assert lerp(10, 20, 0) == 10 and lerp(10, 20, 1) == 20 and lerp(10, 20, 0.25) == 12.5
    assert lerp(5, -5, 0.5) == 0


def test_lerp_point():
    assert lerp_point((0, 0), (4, -2), 0.5) == (2, -1)


@pytest.mark.parametrize("x, out", [(-1, 0), (0.3, 0.3), (7, 1)])
def test_clamp(x, out):
    assert clamp(x, 0, 1) == out


def test_ease():
    assert ease_out_quad(0) == 0 and ease_out_quad(1) == 1 and ease_out_quad(0.5) == 0.75
    assert ease_out_quad(2) == 1 and ease_out_quad(-1) == 0
