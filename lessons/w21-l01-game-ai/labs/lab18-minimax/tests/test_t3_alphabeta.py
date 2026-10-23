from conftest import Budget, random_positions
from search import Stats, ab_best_move, alphabeta, best_move, center_first, minimax


def test_same_value_as_minimax(ttt):
    for s in random_positions(ttt, 40, seed=1, min_moves=2):
        assert alphabeta(ttt, s) == minimax(ttt, s)


def test_prunes_a_lot(ttt):
    full, cut = Stats(), Stats()
    minimax(ttt, ttt.initial(), full)
    assert alphabeta(ttt, ttt.initial(), stats=cut) == 0
    assert cut.nodes * 10 < full.nodes


def test_best_move_same_as_minimax(ttt):
    for s in random_positions(ttt, 20, seed=2, min_moves=3):
        m = ab_best_move(ttt, s)
        p = ttt.to_move(s)
        assert minimax(ttt, ttt.play(s, m)) == minimax(ttt, ttt.play(s, best_move(ttt, s)))
        assert minimax(ttt, ttt.play(s, m)) * p == max(minimax(ttt, ttt.play(s, x)) * p for x in ttt.moves(s))


def test_center_first(c4, small):
    assert center_first(c4, c4.initial(), c4.moves(c4.initial())) == [3, 2, 4, 1, 5, 0, 6]
    assert center_first(small, small.initial(), [0, 1, 2, 3]) == [1, 2, 0, 3]
    assert center_first(c4, c4.initial(), [6, 0, 3]) == [3, 0, 6]


def test_ordering_helps(small):
    plain, ordered = Budget(), Budget()
    v1 = alphabeta(small, small.initial(), stats=plain)
    v2 = alphabeta(small, small.initial(), stats=ordered, order=center_first)
    assert v1 == v2 == 1  # на 4×4 «три в ряд» первый игрок выигрывает
    assert ordered.nodes < plain.nodes
