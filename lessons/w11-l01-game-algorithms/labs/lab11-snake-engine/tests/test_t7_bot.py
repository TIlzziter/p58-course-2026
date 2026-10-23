from bot import ai_move
from engine import DIRS, step
from helpers import board, rng


def play_until_eat(s, name, limit=100):
    score = s.snakes[name].score
    for t in range(1, limit + 1):
        step(s, {name: ai_move(s, name)}, rng())
        assert s.snakes[name].alive, f"погиб на тике {t}"
        if s.snakes[name].score > score:
            return t
    return None


def test_shortest_path_on_empty_board():
    s = board(10, 10, food=(7, 6), a=([(2, 2), (1, 2), (0, 2)], "right"))
    assert play_until_eat(s, "a") == 5 + 4


def test_goes_around_obstacle():
    # b — неподвижная стена x = 4, y = 0..7; хвост (8, 8) в стороне — бот считает хвосты уходящими
    wall = [(4, y) for y in range(8)]
    s = board(9, 9, food=(6, 1), a=([(2, 1), (1, 1), (0, 1)], "right"), b=(wall + [(8, 8)], "down"))
    for t in range(1, 40):
        d = ai_move(s, "a")
        dx, dy = DIRS[d]
        a = s.snakes["a"]
        head = (a.head[0] + dx, a.head[1] + dy)
        assert head not in wall
        a.body, a.direction = [head] + a.body[:-1], d
        if head == s.food:
            break
    assert t == 18                              # 4 вправо + 7 вниз + 7 вверх


def test_eats_ten_in_a_row():
    s = board(10, 10, food=(5, 5), a=([(2, 2), (1, 2), (0, 2)], "right"))
    r = rng(3)
    for _ in range(400):
        step(s, {"a": ai_move(s, "a")}, r)
        assert s.snakes["a"].alive
        if s.snakes["a"].score == 10:
            break
    assert s.snakes["a"].score == 10


def test_never_reverses_or_hits_wall():
    s = board(3, 3, food=None, a=([(2, 0), (1, 0), (0, 0)], "right"))
    assert ai_move(s, "a") == "down"


def test_unreachable_food_safe_move():
    s = board(5, 5, food=(4, 4), a=([(0, 0)], "right"),
              b=([(3, 3), (3, 4), (4, 3), (2, 2), (2, 2)], "up"))
    s.snakes["b"].body = [(4, 3), (3, 3), (3, 4), (2, 0)]     # (4,4) закрыта; хвост (2,0) не мешает
    d = ai_move(s, "a")
    assert d in ("right", "down")
