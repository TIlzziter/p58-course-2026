from predict import Predictor, apply


def test_apply_clamped():
    assert apply((0, 0), "left", 5, 5) == (0, 0) and apply((4, 2), "right", 5, 5) == (4, 2)
    assert apply((1, 1), "down", 5, 5) == (1, 2)


def test_local_moves_immediately():
    p = Predictor((2, 2), 5, 5)
    assert p.local("right") == 1 and p.local("right") == 2
    assert p.pos == (4, 2) and [s for s, _ in p.pending] == [1, 2]


def test_server_confirms():
    p = Predictor((2, 2), 5, 5)
    p.local("right")
    p.local("up")
    p.server((3, 2), last_seq=1)                # сервер обработал первое — второе ещё в пути
    assert p.pos == (3, 1) and [s for s, _ in p.pending] == [2] and p.corrections == 0


def test_server_corrects():
    p = Predictor((2, 2), 5, 5)
    p.local("right")
    p.local("right")
    p.server((2, 2), last_seq=1)                # сервер не пустил вправо (там стена/игрок)
    assert p.pos == (3, 2) and p.corrections == 1


def test_all_acked():
    p = Predictor((0, 0), 3, 3)
    for c in ["down", "down", "right"]:
        p.local(c)
    p.server((1, 2), last_seq=3)
    assert p.pos == (1, 2) and p.pending == []
