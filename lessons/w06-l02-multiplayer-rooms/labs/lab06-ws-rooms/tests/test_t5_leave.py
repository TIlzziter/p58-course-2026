def test_leave_during_game(started):
    started.handle("Аня", {"type": "move", "col": 3})
    out = started.leave("Аня")
    assert out == [("Боря", {"type": "opponent_left", "name": "Аня"}),
                   ("Боря", {"type": "game_over", "result": "win2", "reason": "forfeit"})]
    assert started.handle("Боря", {"type": "move", "col": 2}) == [("Боря", {"type": "error", "code": "game_over"})]


def test_leave_before_start(room):
    room.join("Аня")
    assert room.leave("Аня") == []
    assert room.is_empty
    assert room.join("Боря")[0][1]["color"] == 1


def test_leave_after_game(started):
    for col in [0, 1, 0, 1, 0, 1, 0]:
        started.handle("Аня" if started.game.turn == 1 else "Боря", {"type": "move", "col": col})
    assert started.leave("Боря") == [("Аня", {"type": "opponent_left", "name": "Боря"})]


def test_unknown_and_empty(started):
    assert started.leave("Никто") == []
    started.leave("Аня")
    started.leave("Боря")
    assert started.is_empty
