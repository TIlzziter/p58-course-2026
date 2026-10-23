import json

from connect4 import Game


def test_shape():
    g = Game.from_moves("44")
    s = g.to_json()
    assert set(s) == {"board", "turn", "status", "win_cells", "moves"}
    assert s["turn"] == 1 and s["moves"] == 2 and s["status"] == "playing" and s["win_cells"] == []
    json.dumps(s)


def test_win_cells_for_highlight():
    s = Game.from_moves("4455667").to_json()
    assert s["status"] == "win1"
    assert s["win_cells"] == [[5, 3], [5, 4], [5, 5], [5, 6]]


def test_board_is_copy():
    g = Game.from_moves("1")
    s = g.to_json()
    s["board"][5][0] = 2
    assert g.board[5][0] == 1
