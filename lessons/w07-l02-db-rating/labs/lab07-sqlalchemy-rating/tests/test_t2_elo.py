import random

import elo
import pytest


def test_expected():
    assert elo.expected(1000, 1000) == 0.5
    assert elo.expected(1200, 1000) == pytest.approx(0.7597, abs=1e-4)
    assert elo.expected(1000, 1200) + elo.expected(1200, 1000) == pytest.approx(1)


@pytest.mark.parametrize("ra, rb, score, out", [
    (1000, 1000, 1, (1016, 984)),
    (1000, 1000, 0, (984, 1016)),
    (1000, 1000, 0.5, (1000, 1000)),
    (1200, 1000, 1, (1208, 992)),     # фаворит выиграл — мало
    (1000, 1200, 1, (1024, 1176)),    # победа над сильным — много
    (1200, 1000, 0.5, (1192, 1008)),  # ничья с сильным — плюс слабому
])
def test_update(ra, rb, score, out):
    assert elo.update(ra, rb, score) == out


def test_types_and_k():
    a, b = elo.update(1000, 1000, 1, k=10)
    assert (a, b) == (1005, 995)
    assert type(a) is int and type(b) is int


def test_sum_preserved():
    rnd = random.Random(58)
    for _ in range(300):
        ra, rb = rnd.randint(600, 2400), rnd.randint(600, 2400)
        a, b = elo.update(ra, rb, rnd.choice([0, 0.5, 1]))
        assert a + b == ra + rb


@pytest.mark.parametrize("score", [2, -1, 0.3])
def test_bad_score(score):
    with pytest.raises(ValueError):
        elo.update(1000, 1000, score)
