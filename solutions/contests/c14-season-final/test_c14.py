import pytest
from matchmaking import matchmake, window
from tasks import (
    changelog,
    diff_lines,
    elo,
    latency,
    leaderboard,
    migration_order,
    next_version,
    parse_request,
    scan_secrets,
    seeding,
    semver_sort,
    sign_init_data,
    swiss_pairs,
    validate_move,
    verify_init_data,
    ws_header,
)
from tournament import elo_replay, round_robin, standings

TOKEN = "123456789:AAH-test-token-for-contest-only-0000"  # не настоящий
CM = ["feat(hints): подсказки в партии", "fix: рейтинг при ничьей", "chore: обновить ruff",
      "fix(ws): поле после переподключения"]
RES = [("A", "B", 1), ("C", "D", 0.5), ("A", "C", 0), ("B", "D", 1), ("A", "D", 1), ("B", "C", 1)]


def test_a1():
    assert elo(1500, 1500, 1) == (1516, 1484)
    assert elo(1600, 1400, 0) == (1576, 1424)
    assert elo(1200, 1400, 0.5) == (1208, 1392)


def test_a2():
    assert leaderboard({"ann": 10, "bob": 12, "cid": 10, "dan": 7, "eve": 12}) == [
        (1, "bob", 12), (1, "eve", 12), (3, "ann", 10), (3, "cid", 10), (5, "dan", 7)]
    assert leaderboard({}) == []


def test_a3():
    assert validate_move({"type": "move", "room": "r-1", "cell": 4}) == []
    assert validate_move({"type": "mv", "cell": True, "x": 1, "a": 2}) == [
        "type: неверно", "room: нет", "cell: неверно", "лишний ключ: a", "лишний ключ: x"]
    assert validate_move([1]) == ["не объект"]
    assert validate_move({"type": "move", "room": "R" * 3, "cell": 9}) == ["room: неверно", "cell: неверно"]


def test_a4():
    assert seeding(8) == [1, 8, 4, 5, 2, 7, 3, 6]
    assert seeding(1) == [1] and seeding(2) == [1, 2]
    s = seeding(16)
    assert sorted(s) == list(range(1, 17)) and s.index(2) >= 8
    with pytest.raises(ValueError):
        seeding(6)


def test_b1():
    raw = "GET /api/rooms?page=2&sort=new&page=3 HTTP/1.1\r\nHost: game.example\r\nX-Init-Data: abc\r\n\r\n"
    assert parse_request(raw) == {"method": "GET", "path": "/api/rooms", "query": {"page": "3", "sort": "new"},
                                  "headers": {"host": "game.example", "x-init-data": "abc"}, "body": ""}
    r = parse_request('POST /api/move HTTP/1.1\r\nContent-Type: application/json\r\n\r\n{"cell": 4}')
    assert r["body"] == '{"cell": 4}' and r["query"] == {}
    with pytest.raises(ValueError):
        parse_request("GET /\r\n\r\n")


def test_b2():
    assert ws_header(bytes([0x81, 0x05])) == {"fin": True, "opcode": 1, "masked": False, "length": 5, "header": 2}
    h = ws_header(bytes([0x81, 0xFE, 0x01, 0x00]) + b"k" * 4)
    assert h["masked"] and h["length"] == 256 and h["header"] == 8
    h = ws_header(bytes([0x82, 0x7F]) + (70000).to_bytes(8, "big"))
    assert h["opcode"] == 2 and h["length"] == 70000 and h["header"] == 10
    assert ws_header(bytes([0x08, 0x80]) + b"mask")["fin"] is False
    with pytest.raises(ValueError):
        ws_header(bytes([0x81, 0xFE, 0x01]))


def test_b3():
    fields = {"auth_date": "1777777777", "user": '{"id":58,"first_name":"Аня"}', "query_id": "AAE1"}
    s = sign_init_data(fields, TOKEN)
    assert verify_init_data(s, TOKEN) == fields
    assert verify_init_data(s, TOKEN + "x") is None
    assert verify_init_data(s.replace("58", "59"), TOKEN) is None
    assert verify_init_data("auth_date=1", TOKEN) is None


def test_c1():
    played = {frozenset("ab"), frozenset("cd")}
    assert swiss_pairs({"a": 2, "b": 2, "c": 1, "d": 1, "e": 0, "f": 0}, played) == [
        ("a", "c"), ("b", "d"), ("e", "f")]
    played = {frozenset("ab"), frozenset("ac"), frozenset("cd")}
    assert swiss_pairs({"a": 2, "b": 1, "c": 1, "d": 0}, played) == [("a", "d"), ("b", "c")]
    with pytest.raises(ValueError):
        swiss_pairs({"a": 1, "b": 0}, {frozenset("ab")})


def test_c2():
    g = {"tg": {"nginx": 20}, "nginx": {"api1": 2, "api2": 5}, "api1": {"redis": 1, "pg": 4}, "api2": {"pg": 1},
         "redis": {"pg": 1}}
    assert latency(g, "tg") == {"api1": 22, "api2": 25, "nginx": 20, "pg": 24, "redis": 23, "tg": 0}
    assert latency(g, "pg") == {"pg": 0}


def test_c3():
    assert migration_order({"c3": "b2", "a1": None, "b2": "a1", "d4": "c3"}) == ["a1", "b2", "c3", "d4"]
    for bad in ({"a": None, "b": "a", "c": "a"}, {"a": None, "b": None}, {"a": None, "b": "zz"},
                {"a": None, "b": "c", "c": "b"}):
        with pytest.raises(ValueError):
            migration_order(bad)


def test_c4():
    assert diff_lines(["a", "b", "c", "d"], ["a", "c", "x", "d"]) == ["  a", "- b", "  c", "+ x", "  d"]
    assert diff_lines(["x"], ["y"]) == ["- x", "+ y"]
    assert diff_lines([], ["a"]) == ["+ a"] and diff_lines(["a"], ["a"]) == ["  a"]


def test_d1():
    v = ["1.0.0", "1.0.0-rc1", "0.9.12", "1.0.0-rc10", "1.0.0-rc.2", "1.0.0-rc.10", "1.0.1", "1.0.0-beta"]
    assert semver_sort(v) == ["0.9.12", "1.0.0-beta", "1.0.0-rc.2", "1.0.0-rc.10", "1.0.0-rc1", "1.0.0-rc10",
                              "1.0.0", "1.0.1"]
    assert semver_sort(["v2.0.0", "1.10.0", "1.9.0"]) == ["1.9.0", "1.10.0", "v2.0.0"]
    with pytest.raises(ValueError):
        semver_sort(["1.0"])


def test_d2():
    assert next_version("1.0.0-rc1", CM) == "1.1.0"
    assert next_version("1.2.3", ["fix: x"]) == "1.2.4"
    assert next_version("1.2.3", ["feat!: новый протокол"]) == "2.0.0"
    assert next_version("1.2.3", ["feat: x\n\nBREAKING CHANGE: формат"]) == "2.0.0"
    assert next_version("0.4.1", ["feat: a", "refactor!: b"]) == "0.5.0"
    assert next_version("1.2.3", ["docs: x"]) == "1.2.3"
    assert changelog("1.1.0", "2027-05-20", [*CM, "feat!: ходы в новом формате"]) == (
        "## 1.1.0 — 2027-05-20\n### Ломающее\n- ходы в новом формате\n### Новое\n- hints: подсказки в партии\n"
        "### Исправлено\n- рейтинг при ничьей\n- ws: поле после переподключения")
    assert changelog("1.0.1", "2027-05-21", ["chore: x"]) == "## 1.0.1 — 2027-05-21"


def test_d3():
    fake = "AA" + "x" * 33  # собираем на лету, чтобы сканеры секретов не ругались на репозиторий
    txt = (f"TOKEN=1234567890:{fake}\nDATABASE_URL=postgresql+asyncpg://game:hunter2@db/game\n"
           "DATABASE_URL=postgresql://game:${DB_PASSWORD}@db/game\n-----BEGIN OPENSSH PRIVATE KEY-----\nok")
    assert scan_secrets(txt) == [(1, "telegram"), (2, "dsn_password"), (4, "private_key")]
    assert scan_secrets("BOT_TOKEN=\nredis://redis:6379/0\nurl=postgresql://u:<пароль>@h/db") == []


def test_e4a():
    assert round_robin(["A", "B", "C", "D"]) == [
        [("A", "D"), ("B", "C")], [("A", "C"), ("D", "B")], [("A", "B"), ("C", "D")]]
    assert round_robin(["A", "B", "C"]) == [[("B", "C")], [("A", "C")], [("A", "B")]]
    rr = round_robin([f"p{i}" for i in range(6)])
    pairs = [frozenset(p) for r in rr for p in r]
    assert len(rr) == 5 and len(set(pairs)) == 15


def test_e4b():
    assert standings(RES) == [("A", 6), ("B", 6), ("C", 4), ("D", 1)]
    assert standings([("x", "y", 0.5)]) == [("x", 1), ("y", 1)]


def test_e4c():
    assert elo_replay({"A": 1300}, RES) == {"A": 1302, "B": 1222, "C": 1204, "D": 1172}


def test_e5():
    assert window(0) == 100 and window(19.9) == 150 and window(20) == 200
    ev = [(0, "ann", 1500), (0, "bob", 1720), (2, "cid", 1580), (5, "dan", 1650), (12, "eve", 1500),
          (20, "fay", 1690)]
    assert matchmake(ev, 60) == [(2.0, "ann", "cid", 80), (5.0, "bob", "dan", 70), (40.0, "eve", "fay", 190)]
    assert matchmake([(0, "a", 1000), (0, "b", 1300)], 60) == [(40.0, "a", "b", 300)]
