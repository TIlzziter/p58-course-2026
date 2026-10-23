import random

from mc import mc_move, random_playout


def test_playout_ends_and_deterministic(ttt, c4):
    for seed in range(20):
        w = random_playout(ttt, ttt.initial(), random.Random(seed))
        assert w in (1, -1, 0)
        assert w == random_playout(ttt, ttt.initial(), random.Random(seed))
    assert random_playout(c4, c4.initial(), random.Random(1)) in (1, -1, 0)


def test_playout_of_finished(ttt):
    assert random_playout(ttt, ttt.parse("XXX/OO./..."), random.Random(0)) == 1


def test_playout_uses_rng_choice(ttt):
    s = ttt.parse("XOX/XOO/OX.")
    assert random_playout(ttt, s, random.Random(0)) == 0  # единственный ход 8 — ничья


def test_playout_statistics(ttt):
    rng = random.Random(7)
    res = [random_playout(ttt, ttt.initial(), rng) for _ in range(3000)]
    # при случайной игре X выигрывает ≈ 58 %, O ≈ 29 %, ничьих ≈ 13 %
    assert 0.54 < res.count(1) / 3000 < 0.62
    assert 0.25 < res.count(-1) / 3000 < 0.33


def test_takes_immediate_win(ttt, c4):
    assert mc_move(ttt, ttt.parse("XX./OO./..."), 1, random.Random(0)) == 2
    s = c4.parse("......./......./......./......./OOO..../XXX....")
    assert mc_move(c4, s, 1, random.Random(0)) == 3


def test_blocks(ttt):
    assert mc_move(ttt, ttt.parse("X../OO./X.."), 60, random.Random(2)) == 5
    assert mc_move(ttt, ttt.parse("XX./.O./..."), 60, random.Random(3)) == 2


def test_beats_random(ttt):
    rng = random.Random(11)
    lost = 0
    for g in range(30):
        s, ai = ttt.initial(), 1 if g % 2 == 0 else -1
        while ttt.winner(s) is None:
            m = mc_move(ttt, s, 30, rng) if ttt.to_move(s) == ai else rng.choice(ttt.moves(s))
            s = ttt.play(s, m)
        lost += ttt.winner(s) == -ai
    assert lost <= 2
