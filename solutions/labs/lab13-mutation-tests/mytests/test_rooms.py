import pytest
from game.rooms import NotInRoom, Room, RoomFull


@pytest.fixture
def room():
    r = Room("ABCD", capacity=3)
    for u in ["ann", "bob"]:
        r.join(u)
    return r


def test_join_order_and_host(room):
    assert room.players == ["ann", "bob"] and room.host == "ann"
    assert Room("X").host is None


def test_join_twice(room):
    assert room.join("bob") is False and room.players == ["ann", "bob"]
    assert room.join("cat") is True


def test_full(room):
    room.join("cat")
    with pytest.raises(RoomFull):
        room.join("dan")
    assert len(room.players) == 3
    assert Room("Y").capacity == 4


def test_host_leaves(room):
    room.join("cat")
    room.leave("ann")
    assert room.host == "bob"
    room.leave("bob")
    room.leave("cat")
    assert room.host is None and room.players == []


def test_leave_unknown(room):
    with pytest.raises(NotInRoom):
        room.leave("zed")
    with pytest.raises(NotInRoom):
        room.set_ready("zed")


def test_can_start(room):
    assert not room.can_start()
    room.set_ready("ann")
    assert not room.can_start()
    room.set_ready("bob")
    assert room.can_start()
    room.set_ready("bob", False)
    assert not room.can_start()


def test_alone_cannot_start():
    r = Room("S")
    r.join("ann")
    r.set_ready("ann")
    assert not r.can_start()


def test_leave_clears_ready(room):
    room.set_ready("ann")
    room.set_ready("bob")
    room.leave("bob")
    room.join("bob")
    assert not room.can_start()
