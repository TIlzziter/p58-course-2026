import pytest
from rooms import create_room, invite_link, load_room, room_from_start_param, save_state


async def test_create_load(r):
    await create_room(r, "r1", "c4", ["Аня", "Боря"])
    assert await load_room(r, "r1") == {"game": "c4", "players": ["Аня", "Боря"], "state": {}}
    assert 1790 <= await r.ttl("room:r1") <= 1800
    assert await r.type("room:r1") == "hash"


async def test_duplicate(r):
    await create_room(r, "r1", "c4", ["Аня"])
    with pytest.raises(ValueError):
        await create_room(r, "r1", "snake", ["Боря"])
    assert (await load_room(r, "r1"))["game"] == "c4"


async def test_missing(r):
    assert await load_room(r, "nope") is None
    with pytest.raises(LookupError):
        await save_state(r, "nope", {})


async def test_save_state_refreshes_ttl(r):
    await create_room(r, "r1", "c4", ["Аня", "Боря"], ttl=100)
    await r.expire("room:r1", 3)
    await save_state(r, "r1", {"turn": 2, "board": [[0, 1]]}, ttl=100)
    room = await load_room(r, "r1")
    assert room["state"] == {"turn": 2, "board": [[0, 1]]}
    assert await r.ttl("room:r1") > 90


def test_invite_link():
    assert invite_link("@p58_games_bot", "Ab-3_x") == "https://t.me/p58_games_bot?startapp=room_Ab-3_x"
    for bad in ["", "a b", "комната", "x" * 33, "a/b"]:
        with pytest.raises(ValueError):
            invite_link("bot", bad)


@pytest.mark.parametrize("param, room", [
    ("room_Ab-3_x", "Ab-3_x"), (None, None), ("", None), ("ref_42", None), ("room_", None), ("room_a b", None),
])
def test_start_param(param, room):
    assert room_from_start_param(param) == room
