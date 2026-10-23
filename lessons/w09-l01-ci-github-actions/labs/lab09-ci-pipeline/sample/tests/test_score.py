import pytest

from app.score import combo_bonus, total


def test_bonus():
    assert [combo_bonus(s) for s in range(6)] == [0, 0, 0, 5, 10, 15]
    with pytest.raises(ValueError):
        combo_bonus(-1)


def test_total():
    assert total([]) == 0
    assert total([True, True, True]) == 35
    assert total([True, False, True]) == 20
