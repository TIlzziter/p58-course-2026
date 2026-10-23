from helpers import board, rng

from engine import new_game, place_food, step


def test_eat_grows_and_scores():
    s = board(6, 3, food=(3, 1), a=([(2, 1), (1, 1), (0, 1)], "right"))
    step(s, {}, rng())
    a = s.snakes["a"]
    assert a.body == [(3, 1), (2, 1), (1, 1), (0, 1)] and a.score == 1
    assert s.food is not None and s.food not in a.body
    step(s, {"a": "down"}, rng())
    assert len(s.snakes["a"].body) == 4                         # растёт один раз


def test_food_deterministic():
    a, b = new_game(8, 8, ["x", "y"], rng(42)), new_game(8, 8, ["x", "y"], rng(42))
    assert a.food == b.food


def test_full_board():
    s = board(2, 2, food=None, a=([(0, 0), (1, 0), (1, 1), (0, 1)], "up"))
    assert place_food(s, rng()) is None


def test_only_free_cell():
    s = board(2, 2, food=None, a=([(0, 0), (1, 0), (1, 1)], "up"))
    assert place_food(s, rng()) == (0, 1)


def test_dead_snakes_free_their_cells():
    s = board(2, 1, food=None, a=([(0, 0)], "up"), b=([(1, 0)], "up"))
    s.snakes["b"].alive = False
    assert place_food(s, rng()) == (1, 0)


def test_eater_who_dies_scores_nothing():
    s = board(5, 3, food=(2, 1), a=([(1, 1), (0, 1)], "right"), b=([(3, 1), (4, 1)], "left"))
    step(s, {}, rng())
    assert s.snakes["a"].score == 0 and s.snakes["b"].score == 0 and s.food == (2, 1)
