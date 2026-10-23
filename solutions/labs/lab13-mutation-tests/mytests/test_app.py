import pytest
from fastapi.testclient import TestClient
from game.app import MAX_TEXT, create_app
from starlette.websockets import WebSocketDisconnect


@pytest.fixture
def client():
    with TestClient(create_app()) as c:
        yield c


def hello(ws, name):
    ws.send_json({"type": "hello", "name": name})
    return ws.receive_json()


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_join_and_chat(client):
    with client.websocket_connect("/ws/R1") as a:
        assert hello(a, "ann") == {"type": "joined", "name": "ann", "players": ["ann"]}
        with client.websocket_connect("/ws/R1") as b:
            assert hello(b, "bob")["players"] == ["ann", "bob"]
            assert a.receive_json() == {"type": "joined", "name": "bob", "players": ["ann", "bob"]}
            b.send_json({"type": "chat", "text": "  привет  "})
            assert a.receive_json() == {"type": "chat", "from": "bob", "text": "привет"}
            assert b.receive_json() == {"type": "chat", "from": "bob", "text": "привет"}
        a.send_json({"type": "chat", "text": "эй"})        # чтобы не зависнуть, если left не придёт
        assert a.receive_json() == {"type": "left", "name": "bob", "players": ["ann"]}
        assert a.receive_json()["text"] == "эй"


def test_rooms_isolated(client):
    with client.websocket_connect("/ws/R1") as a, client.websocket_connect("/ws/R2") as b:
        hello(a, "ann")
        hello(b, "bob")
        b.send_json({"type": "chat", "text": "x"})
        assert b.receive_json()["text"] == "x"
        a.send_json({"type": "chat", "text": "y"})
        assert a.receive_json() == {"type": "chat", "from": "ann", "text": "y"}   # не «x»


@pytest.mark.parametrize("first", [{"type": "chat", "text": "hi"}, {"type": "chat", "name": "ann"}, {"type": "hello"},
                                   {"type": "hello", "name": "  "}])
def test_bad_hello(client, first):
    with client.websocket_connect("/ws/R1") as ws:
        ws.send_json(first)
        with pytest.raises(WebSocketDisconnect) as e:
            ws.receive_json()
        assert e.value.code == 4001


def test_name_taken(client):
    with client.websocket_connect("/ws/R1") as a:
        hello(a, "ann")
        with client.websocket_connect("/ws/R1") as b:
            b.send_json({"type": "hello", "name": "ann"})
            with pytest.raises(WebSocketDisconnect) as e:
                b.receive_json()
            assert e.value.code == 4009


def test_empty_and_long(client):
    # читаем сначала у отправителя: если код сломан, тест упадёт, а не зависнет в ожидании
    with client.websocket_connect("/ws/R1") as a, client.websocket_connect("/ws/R1") as b:
        hello(a, "ann")
        hello(b, "bob")
        a.receive_json()                                    # joined bob
        b.send_json({"type": "chat", "text": "   "})
        b.send_json({"type": "chat", "text": "x" * (MAX_TEXT + 1)})
        assert b.receive_json() == {"type": "error", "reason": "too_long"}
        b.send_json({"type": "chat", "text": "y" * MAX_TEXT})
        assert b.receive_json() == {"type": "chat", "from": "bob", "text": "y" * MAX_TEXT}
        assert a.receive_json() == {"type": "chat", "from": "bob", "text": "y" * MAX_TEXT}   # ни пустого, ни ошибки
