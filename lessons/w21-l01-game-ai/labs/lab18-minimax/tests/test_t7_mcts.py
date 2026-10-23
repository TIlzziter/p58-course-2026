import random

from mc import mcts_move


def test_wins_and_blocks(ttt):
    assert mcts_move(ttt, ttt.parse("XX./OO./..."), 300, random.Random(1)) == 2
    assert mcts_move(ttt, ttt.parse("X../OO./X.."), 400, random.Random(2)) == 5


def test_reproducible(ttt):
    a = mcts_move(ttt, ttt.initial(), 200, random.Random(4))
    b = mcts_move(ttt, ttt.initial(), 200, random.Random(4))
    assert a == b


def test_c4_takes_win_and_blocks(c4):
    win = c4.parse("......./......./......./......./OOO..../XXX....")
    assert mcts_move(c4, win, 400, random.Random(5)) == 3
    block = c4.parse("......./......./......./......./......./XXX..OO")
    assert mcts_move(c4, block, 800, random.Random(6)) == 3


def test_never_loses_to_random_ttt(ttt):
    rng = random.Random(9)
    for g in range(10):
        s, ai = ttt.initial(), 1 if g % 2 == 0 else -1
        while ttt.winner(s) is None:
            m = mcts_move(ttt, s, 300, rng) if ttt.to_move(s) == ai else rng.choice(ttt.moves(s))
            s = ttt.play(s, m)
        assert ttt.winner(s) != -ai
