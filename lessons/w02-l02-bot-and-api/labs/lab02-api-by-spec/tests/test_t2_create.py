import pytest


def test_create_room_201(client):
    r = client.post("/rooms", json={"player": "аня"})
    assert r.status_code == 201
    assert r.json() == {"room_id": 1, "players": ["аня"], "board": ".........",
                        "turn": None, "status": "waiting", "winner": None}


def test_ids_increase(client):
    ids = [client.post("/rooms", json={"player": f"p{i}"}).json()["room_id"] for i in range(3)]
    assert ids == [1, 2, 3]


def test_get_room(client):
    client.post("/rooms", json={"player": "аня"})
    assert client.get("/rooms/1").json()["players"] == ["аня"]


def test_unknown_room_404(client):
    r = client.get("/rooms/42")
    assert r.status_code == 404
    assert r.json()["detail"]["code"] == "room_not_found"


@pytest.mark.parametrize("name", ["", " аня", "аня ", "x" * 21])
def test_bad_name_422(client, name):
    assert client.post("/rooms", json={"player": name}).status_code == 422


def test_name_20_chars_ok(client):
    assert client.post("/rooms", json={"player": "x" * 20}).status_code == 201
