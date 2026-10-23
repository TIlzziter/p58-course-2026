from conftest import board_from
from connect4 import new_board, status


def test_playing():
    assert status(new_board()) == "playing"


def test_win2():
    b = board_from("""
        .......
        .......
        .......
        .......
        .......
        oooox..""")
    assert status(b) == "win2"


def test_draw():
    b = board_from("""
        xxoxxox
        ooxooxo
        xxoxxox
        ooxooxo
        xxoxxox
        ooxooxo""")
    assert status(b) == "draw"
