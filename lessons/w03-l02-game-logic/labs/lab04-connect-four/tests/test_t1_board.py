import pytest
from connect4 import new_board


def test_size():
    b = new_board()
    assert len(b) == 6 and all(len(r) == 7 for r in b)
    assert all(v == 0 for r in b for v in r)


def test_rows_independent():
    b = new_board()
    b[5][0] = 1
    assert b[0][0] == 0, "строки — один и тот же список? [[0]*7]*6 копирует ссылку"


def test_custom_size():
    b = new_board(4, 5)
    assert len(b) == 4 and len(b[0]) == 5


def test_too_small():
    with pytest.raises(ValueError):
        new_board(3, 7)
