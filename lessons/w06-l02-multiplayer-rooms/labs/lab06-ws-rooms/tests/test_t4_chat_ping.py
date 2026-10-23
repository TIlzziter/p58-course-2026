def test_ping(started):
    assert started.handle("Боря", {"type": "ping"}) == [("Боря", {"type": "pong"})]


def test_ping_before_start(room):
    room.join("Аня")
    assert room.handle("Аня", {"type": "ping"}) == [("Аня", {"type": "pong"})]


def test_chat(started):
    msg = {"type": "chat", "from": "Боря", "text": "удачи!"}
    assert started.handle("Боря", {"type": "chat", "text": "удачи!"}) == [("Аня", msg), ("Боря", msg)]


def test_chat_does_not_change_turn(started):
    started.handle("Аня", {"type": "chat", "text": "хожу"})
    assert started.game.turn == 1 and started.game.moves == []
