import pytest
from connect4 import Game, MoveError


def test_turns_alternate():
    g = Game()
    g.play(3)
    g.play(3)
    assert g.board[5][3] == 1 and g.board[4][3] == 2
    assert g.turn == 1 and g.moves == [3, 3]


def test_vertical_win_and_game_over():
    g = Game.from_moves("1212121")
    assert g.board[2][0] == 1
    assert g.moves == [0, 1, 0, 1, 0, 1, 0] and g.turn == 2
    with pytest.raises(MoveError) as e:
        g.play(2)
    assert e.value.code == "game_over"


def test_from_moves_status():
    g = Game()
    assert g.play(0) == "playing"
    assert Game.from_moves("4455667").moves == [3, 3, 4, 4, 5, 5, 6]


@pytest.mark.parametrize("bad", ["0", "48a", "9"])
def test_bad_notation(bad):
    with pytest.raises(MoveError):
        Game.from_moves(bad)


def test_undo():
    g = Game.from_moves("443")
    g.undo()
    assert g.moves == [3, 3] and g.board[5][2] == 0 and g.turn == 1
    g.undo()
    g.undo()
    assert g.board[5][3] == 0 and g.turn == 1
    with pytest.raises(MoveError) as e:
        g.undo()
    assert e.value.code == "nothing_to_undo"


def test_undo_after_win_allows_play():
    g = Game.from_moves("1212121")
    g.undo()
    assert g.play(1) == "playing"
