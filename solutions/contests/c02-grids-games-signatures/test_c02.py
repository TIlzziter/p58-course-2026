import hashlib
import hmac
import json
import time
from urllib.parse import urlencode

import app as app_module
import pytest
from fastapi.testclient import TestClient
from minesweeper import GameOver, Minesweeper
from tasks import (
    best_drop,
    click_to_cell,
    column,
    forged,
    fresh,
    gravity,
    k_in_row,
    longest_run,
    next_turn,
    parse_env,
    parse_image,
    parse_port,
    parse_query,
    sign,
)

TOKEN = "123456:TEST-TOKEN-for-c02"


def empty():
    return [[0] * 7 for _ in range(6)]


# ---------- A ----------
def test_a1():
    b = [[0, 0, 0], [1, 0, 2], [2, 1, 1]]
    assert column(b, 0) == [2, 1]
    assert column(b, 1) == [1]
    assert column(b, 2) == [1, 2]
    assert column([[0], [0]], 0) == []


def test_a2():
    b = [[1, 0, 2], [0, 2, 0], [0, 0, 1]]
    assert gravity(b) == [[0, 0, 0], [0, 0, 2], [1, 2, 1]]
    assert b == [[1, 0, 2], [0, 2, 0], [0, 0, 1]], "исходное поле менять нельзя"
    assert gravity([[2], [1], [0]]) == [[0], [2], [1]]


def test_a3():
    assert longest_run([[1, 1, 0, 1], [0, 1, 1, 1], [2, 1, 2, 2]], 1) == 3
    assert longest_run([[1, 1, 0, 1], [0, 1, 1, 1], [2, 1, 2, 2]], 2) == 2
    assert longest_run([[0, 0], [0, 0]], 1) == 0


# ---------- B ----------
def test_b1():
    assert k_in_row(["X.O.", "XO..", "O...", "...."], 3) == "O"
    assert k_in_row(["XXXX", "O...", "O...", "O..."], 4) == "X"
    assert k_in_row(["XO", "OX"], 2) == "X"
    assert k_in_row(["XOX", "OXO", "OXO"], 3) is None
    assert k_in_row(["..X", ".X.", "X.."], 3) == "X"


@pytest.mark.parametrize("b,exp", [("." * 9, "X"), ("XO.X.....", "O"), ("XXO......", "O"),
                                   ("XXX......", "invalid"), ("OO.......", "invalid"), ("O........", "invalid")])
def test_b2(b, exp):
    assert next_turn(b) == exp


def test_b3():
    assert click_to_cell(175, 10, 350, 300, 6, 7) == (0, 3)
    assert click_to_cell(349.9, 299.9, 350, 300, 6, 7) == (5, 6)
    assert click_to_cell(0, 0, 350, 300, 6, 7) == (0, 0)
    assert click_to_cell(350, 0, 350, 300, 6, 7) is None
    assert click_to_cell(-1, 5, 350, 300, 6, 7) is None
    assert click_to_cell(70, 52, 140, 120, 6, 7) == (2, 3)


def test_b4():
    b = empty()
    assert best_drop(b, 1) == 3
    b[5][1] = b[5][2] = b[5][3] = 2
    assert best_drop(b, 1) == 0          # закрыть угрозу (левая из двух)
    b[4][6] = b[3][6] = b[2][6] = 1
    b[5][6] = 2
    assert best_drop(b, 1) == 6          # свой выигрыш важнее
    full = [[1, 2] * 3 + [1] for _ in range(6)]
    assert best_drop(full, 1) is None
    b = empty()
    for r in range(6):
        b[r][3] = 1 + r % 2
    assert best_drop(b, 1) == 2          # центр занят — ближайший слева


# ---------- C ----------
def test_c1():
    assert parse_query("user=%D0%90%D0%BD%D1%8F&msg=hello+world&flag&a=1%3D2") == {
        "user": "Аня", "msg": "hello world", "flag": "", "a": "1=2"}
    assert parse_query("") == {}
    assert parse_query("a=1&&b=2") == {"a": "1", "b": "2"}


def test_c2():
    assert sign("id=42", "secret") == "d04769d2311b20c5a04150ecc123192ce18ba3a6f2fc39d99d2a6e97abe5391e"
    items = [("id=42", sign("id=42", "secret")), ("id=1", sign("id=42", "secret")),
             ("id=7", sign("id=7", "secret").upper()), ("x", "00")]
    assert forged(items, "secret") == [1, 3]
    assert forged([], "k") == []


def test_c3():
    assert fresh([100, 90, 200, 0, 40], 100, 60) == 3
    assert fresh([], 100, 60) == 0
    assert fresh([39], 100, 60) == 0


# ---------- D ----------
def test_d1():
    assert parse_port("8000") == {"ip": None, "host": None, "container": 8000, "proto": "tcp"}
    assert parse_port("8080:80") == {"ip": "0.0.0.0", "host": 8080, "container": 80, "proto": "tcp"}
    assert parse_port("127.0.0.1:5432:5432") == {"ip": "127.0.0.1", "host": 5432, "container": 5432, "proto": "tcp"}
    assert parse_port("53:53/udp")["proto"] == "udp"


@pytest.mark.parametrize("ref,exp", [
    ("python", ("docker.io", "library/python", "latest")),
    ("python:3.12-slim", ("docker.io", "library/python", "3.12-slim")),
    ("ghcr.io/p58/games:v1", ("ghcr.io", "p58/games", "v1")),
    ("localhost:5000/api", ("localhost:5000", "api", "latest")),
    ("registry.example.ru:5000/team/bot:2.0", ("registry.example.ru:5000", "team/bot", "2.0")),
    ("user/app", ("docker.io", "user/app", "latest")),
])
def test_d2(ref, exp):
    assert parse_image(ref) == exp


def test_d3():
    text = ('# x\nexport BOT_TOKEN=123:ABC\nDB_URL="postgresql://u:p@db/game"\nNAME=\'Игры P58\'\n'
            'DEBUG=1 # включить\n\nBROKEN\nHASH="a#b"')
    assert parse_env(text) == {"BOT_TOKEN": "123:ABC", "DB_URL": "postgresql://u:p@db/game", "NAME": "Игры P58",
                               "DEBUG": "1", "HASH": "a#b"}


# ---------- E1 ----------
def init_data(user_id=42, auth_date=None, token=TOKEN):
    fields = {"auth_date": str(auth_date or int(time.time())), "query_id": "AAH",
              "user": json.dumps({"id": user_id, "first_name": "Аня"}, ensure_ascii=False)}
    dcs = "\n".join(f"{k}={v}" for k, v in sorted(fields.items()))
    secret = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    fields["hash"] = hmac.new(secret, dcs.encode(), hashlib.sha256).hexdigest()
    return urlencode(fields)


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("BOT_TOKEN", TOKEN)
    app_module.games.clear()
    return TestClient(app_module.app)


def test_e1(client):
    assert client.post("/check", json={"init_data": init_data()}).json() == {"ok": True, "user_id": 42}
    bad = [init_data(token="1:other"), init_data(auth_date=int(time.time()) - 2 * 86400),
           init_data().replace("42", "43"), "garbage", ""]
    for raw in bad:
        assert client.post("/check", json={"init_data": raw}).json() == {"ok": False, "user_id": None}, raw


# ---------- E4 ----------
def game():
    return Minesweeper(4, 5, {(0, 4), (2, 1)})


def test_e4a():
    g = game()
    assert g.count(1, 0) == 1 and g.count(1, 3) == 1 and g.count(3, 4) == 0 and g.count(1, 1) == 1
    assert g.view() == ["#####"] * 4


def test_e4b():
    g = game()
    assert g.open(3, 4) == 9
    assert g.view() == ["#####", "##111", "##1..", "##1.."]
    assert g.open(3, 4) == 0
    assert g.open(1, 0) == 1
    assert g.status == "playing"
    assert g.open(2, 1) == 0 and g.status == "lost"
    assert g.view()[2][1] == "*" and g.view()[0][4] == "*"
    with pytest.raises(GameOver):
        g.open(0, 0)


def test_e4c():
    g = game()
    assert g.flag(2, 1) is True and g.mines_left() == 1
    assert g.open(2, 1) == 0 and g.status == "playing"     # под флагом не открываем
    assert g.flag(2, 1) is False and g.flag(2, 1) is True
    g.open(3, 4)
    assert g.flag(3, 4) is False                            # открытую не флагуем
    g.open(0, 0)
    assert g.view() == ["...1#", "11111", "#F1..", "##1.."]
    for cell in [(2, 0), (3, 0), (3, 1)]:
        g.open(*cell)
    assert g.status == "won"
    with pytest.raises(GameOver):
        g.flag(0, 4)


# ---------- E5* ----------
def test_e5(client):
    r = client.post("/games", json={"rows": 4, "cols": 5, "mines": [[0, 4], [2, 1]]})
    assert r.status_code == 201
    gid = r.json()["id"]
    assert r.json()["view"] == ["#####"] * 4 and "mines" not in r.json()
    r = client.post(f"/games/{gid}/open", json={"r": 3, "c": 4})
    assert r.json()["view"] == ["#####", "##111", "##1..", "##1.."] and r.json()["status"] == "playing"
    assert client.post(f"/games/{gid}/flag", json={"r": 2, "c": 1}).json()["mines_left"] == 1
    assert client.post(f"/games/{gid}/open", json={"r": 9, "c": 9}).status_code == 422
    assert client.post("/games/999/open", json={"r": 0, "c": 0}).status_code == 404
    assert client.post("/games", json={"rows": 2, "cols": 2, "mines": [[5, 5]]}).status_code == 422
    client.post(f"/games/{gid}/flag", json={"r": 2, "c": 1})
    assert client.post(f"/games/{gid}/open", json={"r": 2, "c": 1}).json()["status"] == "lost"
    assert client.post(f"/games/{gid}/open", json={"r": 0, "c": 0}).status_code == 409
