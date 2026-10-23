from fractions import Fraction

import pytest
from pig import best_hold, expected_hold, expectimax, reach_probability
from solver import solve_connect
from tasks import (
    alphabeta_leaves,
    game_value,
    grid_paths,
    grundy,
    knight_distance,
    losing_positions,
    n_queens,
    nim,
    order_gain,
    principal_variation,
    sliding_2x3,
    subset_sums,
    sum_winner,
    ttt_games,
    zobrist,
    zobrist_move,
    zobrist_table,
)

T = [[3, 5], [2, 9], [0, 1]]
T2 = [[[1, 8], [3, 2]], [[9, 4], [6, 7]]]


def test_a1():
    assert subset_sums([3, 1, 4, 1, 5], 5) == 4
    assert subset_sums([], 0) == 1 and subset_sums([], 3) == 0
    assert subset_sums([2, 2, 2], 4) == 3
    assert subset_sums([1] * 12, 6) == 924


def test_a2():
    assert [n_queens(n) for n in range(1, 9)] == [1, 0, 0, 2, 10, 4, 40, 92]


def test_a3():
    assert knight_distance("a1", "b3") == 1 and knight_distance("a1", "h8") == 6
    assert knight_distance("a1", "b2") == 4 and knight_distance("e4", "e4") == 0
    assert knight_distance("h8", "a1") == 6


def test_a4():
    assert sliding_2x3("12345_") == 0 and sliding_2x3("1234_5") == 1
    assert sliding_2x3("_12345") == 15
    assert sliding_2x3("21345_") == -1 and sliding_2x3("4123_5") == -1


def test_b1():
    assert nim([3, 4, 5]) == ("first", (0, 1))
    assert nim([1, 2, 3]) == ("second", None)
    assert nim([7]) == ("first", (0, 0)) and nim([]) == ("second", None)
    assert nim([5, 5, 1]) == ("first", (0, 4))


def test_b2():
    assert game_value(T) == 3 and game_value(T2) == 7
    assert game_value(5) == 5 and game_value([[1, 2]]) == 1
    assert game_value(T, maximizing=False) == 1


def test_b3():
    assert alphabeta_leaves(T) == [3, 5, 2, 0]
    assert alphabeta_leaves(T2) == [1, 8, 3, 2, 9, 4, 6, 7]
    assert alphabeta_leaves([[5, 6], [7, 4, 5], [3, 1]]) == [5, 6, 7, 4, 3]


def test_c1():
    assert ttt_games() == {"total": 255168, "x": 131184, "o": 77904, "draw": 46080}


def test_c2():
    assert losing_positions(20, {1, 3, 4}) == [0, 2, 7, 9, 14, 16]
    assert losing_positions(10, {1, 2}) == [0, 3, 6, 9]
    assert losing_positions(3, {2}) == [0, 1]


def test_c3():
    assert grundy(10, {1, 3, 4}) == [0, 1, 0, 1, 2, 3, 2, 0, 1, 0, 1]
    assert sum_winner([2, 7], {1, 3, 4}) == "second"
    assert sum_winner([3, 5, 6], {1, 2}) == "first"
    assert sum_winner([], {1}) == "second"
    assert sum_winner([4, 4], {1, 2, 3}) == "second"


def test_c4():
    assert principal_variation(T) == [0, 0]
    assert principal_variation(T2) == [1, 1, 1]
    assert principal_variation(4) == []
    assert principal_variation([[2, 2], [2, 1]]) == [0, 0]


def test_d1():
    assert grid_paths(["...", "...", "..."]) == 6
    assert grid_paths(["..#", "...", "#.."]) == 4
    assert grid_paths(["#"]) == 0 and grid_paths(["."]) == 1
    assert grid_paths(["." * 16] * 16) == 155117520


def test_d2():
    t = zobrist_table(9, 2)
    assert len(t) == 9 and len(t[0]) == 2
    b = [1, 0, 0, 0, 2, 0, 0, 0, 0]
    h = zobrist(b, t)
    assert h == 0x414F0E3A63D72D85
    b2 = b[:]
    b2[8] = 1
    assert zobrist(b2, t) == zobrist_move(h, 8, 0, 1, t)
    assert zobrist_move(zobrist_move(h, 4, 2, 1, t), 4, 1, 2, t) == h
    assert zobrist([0] * 9, t) == 0


def test_d3():
    assert order_gain(T2) == (8, 5)
    assert order_gain(T) == (4, 4)
    plain, ordered = order_gain([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    assert ordered < plain


def test_e4a():
    h = Fraction(1, 2)
    assert expectimax(("max", [("chance", [(h, 10), (h, 0)]), ("min", [4, 7])])) == 5
    assert expectimax(("chance", [(Fraction(1, 3), 3), (Fraction(2, 3), ("max", [0, 6]))])) == 5
    assert expectimax(7) == 7
    with pytest.raises(ValueError):
        expectimax(("chance", [(h, 1)]))


def test_e4b():
    assert reach_probability(2) == Fraction(5, 6)
    assert reach_probability(20) == Fraction(5675645, 15116544)
    assert reach_probability(0) == 1


def test_e4c():
    assert expected_hold(20) == Fraction(492303203, 60466176)
    assert expected_hold(2) == Fraction(10, 3)
    assert best_hold() == [20, 21]


def test_e5():
    assert solve_connect(3, 3, 3) == 0
    assert solve_connect(4, 3, 3) == 1
    assert solve_connect(4, 4, 3) == 1
    assert solve_connect(4, 4, 4) == 0
