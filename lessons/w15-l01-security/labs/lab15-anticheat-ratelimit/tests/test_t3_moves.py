from anticheat import MoveValidator


def test_bounds():
    v = MoveValidator(20, 10, max_speed=5)
    assert v.check("ann", 0, 19.5, 9.9) is None
    for x, y in ((20, 5), (-0.1, 5), (5, 10), (5, -1)):
        assert v.check("bob", 0, x, y) == "out_of_bounds"


def test_speed():
    v = MoveValidator(100, 100, max_speed=5)
    assert v.check("ann", 0.0, 0, 0) is None
    assert v.check("ann", 1.0, 3, 4) is None          # 5 клеток за 1 с — можно
    assert v.check("ann", 2.0, 3, 9.5) is None        # 5.5 — в пределах допуска 10 %
    assert v.check("ann", 3.0, 3, 15.1) == "too_fast"  # 5.6 — нет
    assert v.check("ann", 4.0, 3, 15.1) is None       # от последней ПРИНЯТОЙ точки (3, 9.5) за 2 с


def test_stale_and_order():
    v = MoveValidator(100, 100, max_speed=5)
    v.check("ann", 10.0, 0, 0)
    assert v.check("ann", 10.0, 1, 0) == "stale"
    assert v.check("ann", 9.0, 1, 0) == "stale"
    assert v.check("ann", 9.0, 500, 0) == "out_of_bounds"   # поле проверяем первым
    assert v.check("bob", 1.0, 50, 50) is None        # у каждого игрока своя история


def test_rejected_move_keeps_state():
    v = MoveValidator(100, 100, max_speed=1, tolerance=0)
    v.check("ann", 0, 0, 0)
    assert v.check("ann", 1, 50, 0) == "too_fast"     # телепорт
    assert v.check("ann", 2, 2, 0) is None            # считаем от (0, 0) в t = 0
