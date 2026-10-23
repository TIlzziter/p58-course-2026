from game.rooms import Room


def test_first_is_host():
    r = Room("ABCD")
    r.join("ann")
    assert r.host == "ann"
