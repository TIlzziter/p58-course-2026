import pytest

from conftest import play


def code(r):
    return r.json()["detail"]["code"]


def test_move_alternates(playing):
    r = play(playing, [("аня", 4)])
    assert r.json()["board"] == "....X...."
    assert r.json()["turn"] == "боря"
    r = play(playing, [("боря", 0)])
    assert r.json()["board"] == "O...X...."
    assert r.json()["turn"] == "аня"


def test_not_your_turn(playing):
    r = playing.post("/rooms/1/moves", json={"player": "боря", "cell": 0})
    assert r.status_code == 409 and code(r) == "not_your_turn"
    assert playing.get("/rooms/1").json()["board"] == "........."


def test_cell_taken(playing):
    play(playing, [("аня", 4)])
    r = playing.post("/rooms/1/moves", json={"player": "боря", "cell": 4})
    assert r.status_code == 409 and code(r) == "cell_taken"
    assert playing.get("/rooms/1").json()["turn"] == "боря"


def test_not_a_player(playing):
    r = playing.post("/rooms/1/moves", json={"player": "вика", "cell": 0})
    assert r.status_code == 403 and code(r) == "not_a_player"


def test_waiting_room(client):
    client.post("/rooms", json={"player": "аня"})
    r = client.post("/rooms/1/moves", json={"player": "аня", "cell": 0})
    assert r.status_code == 409 and code(r) == "not_playing"


def test_unknown_room(client):
    r = client.post("/rooms/9/moves", json={"player": "аня", "cell": 0})
    assert r.status_code == 404 and code(r) == "room_not_found"


@pytest.mark.parametrize("cell", [-1, 9, 100])
def test_cell_range(playing, cell):
    assert playing.post("/rooms/1/moves", json={"player": "аня", "cell": cell}).status_code == 422
