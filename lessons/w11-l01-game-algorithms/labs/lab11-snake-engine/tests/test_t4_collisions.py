from helpers import board, rng

from engine import step


def alive(s):
    return {n for n, sn in s.snakes.items() if sn.alive}


def test_wall():
    s = board(4, 3, food=(0, 0), a=([(3, 1), (2, 1)], "right"))
    step(s, {}, rng())
    assert alive(s) == set() and s.snakes["a"].body == [(3, 1), (2, 1)]   # тело не уезжает в стену


def test_self():
    #  ряд 1: голова (2,1) идёт вниз в (2,2), а (2,2) — середина тела
    s = board(5, 5, food=(4, 4), a=([(2, 1), (1, 1), (1, 2), (2, 2), (3, 2)], "right"))
    step(s, {"a": "down"}, rng())
    assert alive(s) == set()


def test_own_tail_is_free():
    # квадрат 2×2: голова идёт в клетку, откуда в этот же тик уходит хвост
    s = board(4, 4, food=(3, 3), a=([(1, 0), (1, 1), (0, 1), (0, 0)], "up"))
    step(s, {"a": "left"}, rng())
    assert alive(s) == {"a"} and s.snakes["a"].head == (0, 0)


def test_other_body():
    s = board(6, 5, food=(5, 4), a=([(1, 2), (0, 2)], "right"),
              b=([(2, 3), (2, 2), (2, 1), (2, 0)], "down"))
    step(s, {}, rng())                          # b уходит вниз, но (2,2) остаётся телом b
    assert alive(s) == {"b"}


def test_head_to_head():
    s = board(7, 3, food=(6, 2), a=([(2, 1), (1, 1)], "right"), b=([(4, 1), (5, 1)], "left"))
    step(s, {}, rng())
    assert alive(s) == set()


def test_head_swap():
    s = board(7, 3, food=(6, 2), a=([(2, 1), (1, 1)], "right"), b=([(3, 1), (4, 1)], "left"))
    step(s, {}, rng())
    assert alive(s) == set()


def test_others_tail_is_free():
    s = board(6, 4, food=(5, 3), a=([(1, 1), (0, 1)], "right"), b=([(3, 2), (3, 1), (2, 1)], "down"))
    step(s, {}, rng())                          # a идёт в (2,1) — хвост b оттуда уходит
    assert alive(s) == {"a", "b"}


def test_dead_snake_is_not_obstacle():
    s = board(6, 3, food=(5, 2), a=([(1, 1), (0, 1)], "right"), b=([(2, 1), (3, 1), (4, 1)], "left"))
    s.snakes["b"].alive = False
    step(s, {}, rng())
    assert alive(s) == {"a"}


def test_events():
    s = board(7, 3, food=(6, 2), a=([(2, 1), (1, 1)], "right"), b=([(4, 1), (5, 1)], "left"),
              c=([(0, 0), (0, 1)], "left"))
    step(s, {}, rng())
    assert sorted(s.events) == ["1:a:head", "1:b:head", "1:c:wall"]
