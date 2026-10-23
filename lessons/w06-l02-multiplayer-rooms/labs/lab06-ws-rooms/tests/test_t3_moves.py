from conftest import types


def test_not_started(room):
    room.join("Аня")
    assert room.handle("Аня", {"type": "move", "col": 3}) == [("Аня", {"type": "error", "code": "not_started"})]


def test_move_broadcast(started):
    out = started.handle("Аня", {"type": "move", "col": 3})
    assert types(out) == [("Аня", "state"), ("Боря", "state")]
    msg = out[0][1]
    assert msg["last"] == {"col": 3, "by": 1}
    assert msg["state"]["board"][5][3] == 1 and msg["state"]["turn"] == 2
    assert out[0][1] == out[1][1]


def test_not_your_turn(started):
    assert started.handle("Боря", {"type": "move", "col": 3}) == [("Боря", {"type": "error", "code": "not_your_turn"})]
    started.handle("Аня", {"type": "move", "col": 3})
    assert started.handle("Аня", {"type": "move", "col": 3}) == [("Аня", {"type": "error", "code": "not_your_turn"})]
    assert started.game.moves == [3]


def test_column_full(started):
    for i in range(6):
        started.handle("Аня" if i % 2 == 0 else "Боря", {"type": "move", "col": 0})
    assert started.handle("Аня", {"type": "move", "col": 0}) == [("Аня", {"type": "error", "code": "column_full"})]


def test_game_over(started):
    for col in [0, 1, 0, 1, 0, 1]:
        started.handle("Аня" if started.game.turn == 1 else "Боря", {"type": "move", "col": col})
    out = started.handle("Аня", {"type": "move", "col": 0})
    assert types(out) == [("Аня", "state"), ("Боря", "state"), ("Аня", "game_over"), ("Боря", "game_over")]
    assert out[2][1] == {"type": "game_over", "result": "win1"}
    assert started.handle("Боря", {"type": "move", "col": 1}) == [("Боря", {"type": "error", "code": "game_over"})]
