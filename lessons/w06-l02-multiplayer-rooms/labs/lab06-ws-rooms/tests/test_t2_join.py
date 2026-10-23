import pytest
from conftest import types

from rooms import RoomError


def test_first_player(room):
    out = room.join("Аня")
    assert out == [("Аня", {"type": "welcome", "room": "r1", "color": 1})]
    assert room.players == {"Аня": 1} and not room.started


def test_second_player_starts(room):
    room.join("Аня")
    out = room.join("Боря")
    assert out[0] == ("Боря", {"type": "welcome", "room": "r1", "color": 2})
    assert types(out[1:]) == [("Аня", "start"), ("Боря", "start")]
    start = out[1][1]
    assert start["players"] == {"1": "Аня", "2": "Боря"}
    assert start["state"]["turn"] == 1 and start["state"]["moves"] == 0
    assert room.started


def test_room_full(started):
    with pytest.raises(RoomError) as e:
        started.join("Вика")
    assert e.value.code == "room_full"


def test_name_taken(room):
    room.join("Аня")
    with pytest.raises(RoomError) as e:
        room.join("Аня")
    assert e.value.code == "name_taken"
    assert room.players == {"Аня": 1}
