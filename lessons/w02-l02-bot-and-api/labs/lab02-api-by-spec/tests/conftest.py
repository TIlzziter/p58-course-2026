import pytest
from app import main
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    main.rooms.clear()
    return TestClient(main.app)


@pytest.fixture
def playing(client):
    """Комната 1: аня (X) против бори (O), ходит аня."""
    client.post("/rooms", json={"player": "аня"})
    client.post("/rooms/1/join", json={"player": "боря"})
    return client


def play(client, moves, room=1):
    """Сделать ходы [(игрок, клетка), ...], вернуть последний ответ."""
    r = None
    for player, cell in moves:
        r = client.post(f"/rooms/{room}/moves", json={"player": player, "cell": cell})
        assert r.status_code == 200, r.text
    return r
