def test_game_over_websocket(client):
    with client.websocket_connect("/ws/g1?name=Аня") as a:
        assert a.receive_json() == {"type": "welcome", "room": "g1", "color": 1}
        with client.websocket_connect("/ws/g1?name=Боря") as b:
            assert b.receive_json()["color"] == 2
            assert a.receive_json()["type"] == "start"
            assert b.receive_json()["type"] == "start"
            a.send_json({"type": "move", "col": 3})
            sa, sb = a.receive_json(), b.receive_json()
            assert sa == sb and sa["type"] == "state" and sa["state"]["board"][5][3] == 1


def test_errors_do_not_close(client):
    with client.websocket_connect("/ws/g2?name=Аня") as a:
        a.receive_json()
        a.send_text("не json")
        assert a.receive_json() == {"type": "error", "code": "bad_json"}
        a.send_json({"type": "move", "col": 3})
        assert a.receive_json() == {"type": "error", "code": "not_started"}
        a.send_json({"type": "ping"})
        assert a.receive_json() == {"type": "pong"}


def test_full_room(client):
    with client.websocket_connect("/ws/g3?name=Аня") as a, client.websocket_connect("/ws/g3?name=Боря") as b:
        a.receive_json(), a.receive_json(), b.receive_json(), b.receive_json()
        with client.websocket_connect("/ws/g3?name=Вика") as v:
            assert v.receive_json() == {"type": "error", "code": "room_full"}


def test_disconnect_notifies(client):
    import app as app_module
    with client.websocket_connect("/ws/g4?name=Аня") as a:
        a.receive_json()
        with client.websocket_connect("/ws/g4?name=Боря") as b:
            b.receive_json(), b.receive_json(), a.receive_json()
        assert a.receive_json() == {"type": "opponent_left", "name": "Боря"}
        assert a.receive_json()["reason"] == "forfeit"
    assert "g4" not in app_module.rooms, "пустую комнату надо удалить"


def test_no_name(client):
    with client.websocket_connect("/ws/g5") as a:
        assert a.receive_json() == {"type": "error", "code": "no_name"}
