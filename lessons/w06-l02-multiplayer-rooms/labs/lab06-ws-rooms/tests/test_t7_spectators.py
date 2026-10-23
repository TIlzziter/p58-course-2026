from conftest import types


def test_spectator_join(started):
    out = started.join("Зритель", spectator=True)
    assert out[0][0] == "Зритель"
    assert out[0][1]["type"] == "welcome" and out[0][1]["color"] == 0 and "state" in out[0][1]
    assert started.players == {"Аня": 1, "Боря": 2}


def test_spectator_gets_broadcast_and_cannot_move(started):
    started.join("Зритель", spectator=True)
    out = started.handle("Аня", {"type": "move", "col": 3})
    assert types(out) == [("Аня", "state"), ("Боря", "state"), ("Зритель", "state")]
    assert started.handle("Зритель", {"type": "move", "col": 3}) == [("Зритель", {"type": "error", "code": "spectator"})]
    assert types(started.handle("Зритель", {"type": "chat", "text": "ура"})) == [
        ("Аня", "chat"), ("Боря", "chat"), ("Зритель", "chat")]


def test_spectator_leave(started):
    started.join("Зритель", spectator=True)
    assert started.leave("Зритель") == []
    assert started.everyone() == ["Аня", "Боря"]


def test_spectator_websocket(client):
    with client.websocket_connect("/ws/s1?name=Аня") as a, client.websocket_connect("/ws/s1?name=Боря") as b:
        a.receive_json(), a.receive_json(), b.receive_json(), b.receive_json()
        with client.websocket_connect("/ws/s1?name=Вика&watch=true") as v:
            assert v.receive_json()["color"] == 0
            a.send_json({"type": "move", "col": 2})
            assert v.receive_json()["last"] == {"col": 2, "by": 1}
