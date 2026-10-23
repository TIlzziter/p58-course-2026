import pytest

from connect4 import MoveError, drop, new_board


def test_falls_to_bottom():
    b = new_board()
    assert drop(b, 3, 1) == 5
    assert drop(b, 3, 2) == 4
    assert b[5][3] == 1 and b[4][3] == 2 and b[0][3] == 0


def test_column_full():
    b = new_board()
    for i in range(6):
        drop(b, 0, 1 + i % 2)
    with pytest.raises(MoveError) as e:
        drop(b, 0, 1)
    assert e.value.code == "column_full"


@pytest.mark.parametrize("col", [-1, 7, 100])
def test_bad_column(col):
    with pytest.raises(MoveError) as e:
        drop(new_board(), col, 1)
    assert e.value.code == "bad_column"


def test_bad_player():
    with pytest.raises(ValueError):
        drop(new_board(), 0, 3)
