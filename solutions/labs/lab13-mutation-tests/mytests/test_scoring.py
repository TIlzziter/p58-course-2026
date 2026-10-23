import pytest
from game.scoring import elo, points, streak_bonus


@pytest.mark.parametrize("players, expected", [(2, [3, 0]), (3, [4, 1, 0]), (4, [5, 2, 1, 0])])
def test_points_all_places(players, expected):
    assert [points(p, players) for p in range(1, players + 1)] == expected


@pytest.mark.parametrize("place, players", [(0, 2), (3, 2), (5, 4), (1, 1), (1, 5), (-1, 3)])
def test_points_bad(place, players):
    with pytest.raises(ValueError):
        points(place, players)


@pytest.mark.parametrize("results, bonus", [
    ([], 0), ([True, True], 0), ([True] * 3, 5), ([True] * 4, 10), ([True] * 7, 25), ([True] * 8, 25),
    ([True] * 10 + [False], 0), ([False, True, True, True], 5), ([True, True, False, True, True], 0),
])
def test_streak(results, bonus):
    assert streak_bonus(results) == bonus


def test_elo_equal():
    assert elo(1200, 1200, 1) == (1216, 1184)
    assert elo(1200, 1200, 0) == (1184, 1216)
    assert elo(1200, 1200, 0.5) == (1200, 1200)


def test_elo_favourite_and_k():
    assert elo(1600, 1200, 1) == (1603, 1197)       # фаворит выиграл — почти ничего
    assert elo(1200, 1600, 1) == (1229, 1571)       # аутсайдер выиграл — много
    assert elo(1200, 1200, 1, k=16) == (1208, 1192)
    assert elo(1500, 1400, 0.5) == (1496, 1404)


def test_elo_sum_and_bad():
    a, b = elo(1337, 1111, 0)
    assert a + b == 1337 + 1111
    with pytest.raises(ValueError):
        elo(1200, 1200, 2)
