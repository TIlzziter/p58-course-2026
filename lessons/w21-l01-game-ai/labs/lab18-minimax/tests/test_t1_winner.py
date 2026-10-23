from games import ConnectFour


def test_empty_and_ongoing(c4):
    assert c4.winner(c4.initial()) is None
    s = c4.parse("......./......./......./......./......./XXX.OOO")
    assert c4.winner(s) is None


def test_horizontal_vertical(c4):
    assert c4.winner(c4.parse("......./......./......./......./OOO..../XXXX...")) == 1
    assert c4.winner(c4.parse("......./......./O....../O....../OX...../OXX.X..")) == -1
    assert c4.winner(c4.parse("......./......./......./......./OOO..../...XXXX")) == 1


def test_diagonals(c4):
    up = c4.parse("......./......./...X.../..XO.../.XOO.../XOOX.X.")
    assert c4.winner(up) == 1
    down = c4.parse("......./......./O....../XO...../XXO..X./XXXO.O.")
    assert c4.winner(down) == -1


def test_no_wrap_around(c4):
    # 5, 6 в первом ряду и 0, 1 во втором — не четыре подряд
    s = c4.parse("......./......./......./......./XX..OO./OO..OXX")
    assert c4.winner(s) is None


def test_small_board_and_draw():
    g = ConnectFour(3, 3, 3)
    assert g.winner(g.parse(".../.../XXX")) == 1
    assert g.winner(g.parse("..O/.OX/OXX")) == -1
    assert g.winner(g.parse("XOX/XOX/OXO")) == 0
    assert g.winner(g.parse("X../O../X..")) is None


def test_moves_after_win_empty(c4):
    s = c4.parse("......./......./......./......./OOO..../XXXX...")
    assert c4.moves(s) == []
