import pytest
from interp import blend


def test_both_lerp():
    assert blend({"a": (0, 0)}, {"a": (1, 0)}, 0.25) == {"a": (0.25, 0)}


def test_appear_and_disappear():
    out = blend({"a": (0, 0), "gone": (5, 5)}, {"a": (0, 1), "new": (3, 3)}, 0.5)
    assert out == {"a": (0, 0.5), "new": (3.0, 3.0)}


def test_teleport_no_lerp():
    # змейка прошла через портал / респаун: не «проезжаем» через всё поле
    assert blend({"a": (0, 0)}, {"a": (9, 0)}, 0.4) == {"a": (0.0, 0.0)}
    assert blend({"a": (0, 0)}, {"a": (9, 0)}, 0.5) == {"a": (9.0, 0.0)}
    assert blend({"a": (0, 0)}, {"a": (2, 0)}, 0.5) == {"a": (1, 0)}           # ровно 2 — ещё не прыжок


def test_custom_threshold():
    out = blend({"a": (0, 0)}, {"a": (3, 4)}, 0.2, teleport=10)["a"]
    assert out == pytest.approx((0.6, 0.8))
