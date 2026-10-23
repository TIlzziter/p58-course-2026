import pytest
from app import game
from conftest import play


@pytest.mark.parametrize("board,expected", [
    ("XXX......", "X"), ("...OOO...", "O"), ("X..X..X..", "X"), (".O..O..O.", "O"),
    ("X...X...X", "X"), ("..O.O.O..", "O"), (".........", None), ("XOXOXOOXO", None),
])
def test_winner(board, expected):
    assert game.winner(board) == expected


def test_is_draw():
    assert game.is_draw("XOXXOOOXX")
    assert not game.is_draw("XXX.OO...")
    assert not game.is_draw("XXXOOXOXO")      # заполнено, но есть победитель


def test_place_taken():
    with pytest.raises(ValueError):
        game.place("X........", 0, "O")


def test_win_finishes_game(playing):
    r = play(playing, [("аня", 0), ("боря", 3), ("аня", 1), ("боря", 4), ("аня", 2)])
    assert r.json()["status"] == "finished"
    assert r.json()["winner"] == "аня"
    assert r.json()["turn"] is None
    r = playing.post("/rooms/1/moves", json={"player": "боря", "cell": 5})
    assert r.status_code == 409 and r.json()["detail"]["code"] == "not_playing"


def test_second_player_wins_diagonal(playing):
    r = play(playing, [("аня", 0), ("боря", 2), ("аня", 1), ("боря", 4), ("аня", 8), ("боря", 6)])
    assert r.json()["winner"] == "боря"


def test_draw(playing):
    # X O X / X O O / O X X
    moves = [("аня", 0), ("боря", 1), ("аня", 2), ("боря", 4), ("аня", 3),
             ("боря", 5), ("аня", 7), ("боря", 6), ("аня", 8)]
    r = play(playing, moves)
    assert r.json()["board"] == "XOXXOOOXX"
    assert r.json()["status"] == "finished"
    assert r.json()["winner"] is None and r.json()["turn"] is None
