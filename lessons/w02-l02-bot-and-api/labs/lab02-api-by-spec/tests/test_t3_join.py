def test_join_starts_game(client):
    client.post("/rooms", json={"player": "аня"})
    r = client.post("/rooms/1/join", json={"player": "боря"})
    assert r.status_code == 200
    body = r.json()
    assert body["players"] == ["аня", "боря"]
    assert body["status"] == "playing"
    assert body["turn"] == "аня"


def test_join_unknown_room(client):
    r = client.post("/rooms/5/join", json={"player": "боря"})
    assert r.status_code == 404
    assert r.json()["detail"]["code"] == "room_not_found"


def test_join_full(playing):
    r = playing.post("/rooms/1/join", json={"player": "вика"})
    assert r.status_code == 409
    assert r.json()["detail"]["code"] == "room_full"
    assert playing.get("/rooms/1").json()["players"] == ["аня", "боря"]


def test_join_same_name(client):
    client.post("/rooms", json={"player": "аня"})
    r = client.post("/rooms/1/join", json={"player": "аня"})
    assert r.status_code == 409
    assert r.json()["detail"]["code"] == "name_taken"
    assert client.get("/rooms/1").json()["status"] == "waiting"
