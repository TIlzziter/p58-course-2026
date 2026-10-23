from conftest import board_from
from connect4 import legal_moves, new_board


def test_all_free():
    assert legal_moves(new_board()) == list(range(7))


def test_full_columns_excluded():
    b = board_from("""
        x.o...x
        o.x...o
        x.o...x
        o.x...o
        x.o...x
        o.x...o
    """)
    assert legal_moves(b) == [1, 3, 4, 5]
