import pytest
from engine import new_game, step, turn
from helpers import board, rng


@pytest.mark.parametrize("cur, want, out", [
    ("right", "up", "up"), ("right", "left", "right"), ("up", "down", "up"), ("left", None, "left"),
    ("down", "down", "down"),
])
def test_turn(cur, want, out):
    assert turn(cur, want) == out


def test_turn_bad():
    with pytest.raises(ValueError):
        turn("up", "north")


def test_move_forward():
    s = board(6, 4, food=(5, 3), a=([(2, 1), (1, 1), (0, 1)], "right"))
    step(s, {}, rng())
    assert s.snakes["a"].body == [(3, 1), (2, 1), (1, 1)] and s.tick == 1


def test_move_turn_and_reverse_ignored():
    s = board(6, 4, food=(5, 3), a=([(2, 1), (1, 1), (0, 1)], "right"))
    step(s, {"a": "left"}, rng())               # разворот на 180° игнорируем
    assert s.snakes["a"].head == (3, 1)
    step(s, {"a": "down"}, rng())
    assert s.snakes["a"].body == [(3, 2), (3, 1), (2, 1)] and s.snakes["a"].direction == "down"


def test_new_game():
    s = new_game(10, 9, ["a", "b"], rng())
    assert s.snakes["a"].body == [(2, 3), (1, 3), (0, 3)] and s.snakes["a"].direction == "right"
    assert s.snakes["b"].body == [(7, 6), (8, 6), (9, 6)] and s.snakes["b"].direction == "left"
    assert s.food is not None and s.food not in s.snakes["a"].body + s.snakes["b"].body
