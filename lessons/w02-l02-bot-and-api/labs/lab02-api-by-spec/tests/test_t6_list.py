def test_list_all_sorted(client):
    for name in ["аня", "боря", "вика"]:
        client.post("/rooms", json={"player": name})
    client.post("/rooms/2/join", json={"player": "гоша"})
    rooms = client.get("/rooms").json()
    assert [r["room_id"] for r in rooms] == [1, 2, 3]


def test_filter_by_status(client):
    for name in ["аня", "боря", "вика"]:
        client.post("/rooms", json={"player": name})
    client.post("/rooms/2/join", json={"player": "гоша"})
    assert [r["room_id"] for r in client.get("/rooms", params={"status": "waiting"}).json()] == [1, 3]
    assert [r["room_id"] for r in client.get("/rooms", params={"status": "playing"}).json()] == [2]
    assert client.get("/rooms", params={"status": "finished"}).json() == []


def test_bad_status_422(client):
    assert client.get("/rooms", params={"status": "lost"}).status_code == 422
