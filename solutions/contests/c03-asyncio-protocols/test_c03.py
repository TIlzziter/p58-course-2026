import asyncio
import time

import anyio
import app as app_module
import pytest
from battleship import Battle, Fleet, ShotError, next_shot
from fastapi.testclient import TestClient
from starlette.testclient import WebSocketTestSession
from tasks import (
    assign_rooms,
    count_types,
    decode_frames,
    double_all,
    encode_frame,
    first_answer,
    first_out_of_turn,
    limited,
    matchmake,
    max_online,
    split_stream,
    with_timeout,
)


def _receive(self, timeout=3.0):
    async def get():
        with anyio.fail_after(timeout):
            return await self._send_rx.receive()
    return self.portal.call(get)


WebSocketTestSession.receive = _receive


# ---------- A ----------
def test_a1():
    log = ['{"type": "move", "col": 3}', '{"type": "ping"}', 'oops', '{"type": "move", "col": 1}', '[1]',
           '{"col": 1}', '{"type": 5}']
    assert count_types(log) == {"invalid": 4, "move": 2, "ping": 1}
    assert count_types([]) == {}


def test_a2():
    assert split_stream(['{"a":', '1}\n{"b"', ':2}\n{"c"']) == ['{"a":1}', '{"b":2}']
    assert split_stream(["x\n\ny\n"]) == ["x", "y"]
    assert split_stream(["нет конца"]) == []


def test_a3():
    assert encode_frame("hi") == b"\x00\x02hi"
    assert encode_frame("Ая") == b"\x00\x04" + "Ая".encode()
    data = encode_frame("ход 3") + encode_frame("") + encode_frame("ок")
    assert decode_frames(data) == ["ход 3", "", "ок"]
    assert decode_frames(data + b"\x00\x05ab") == ["ход 3", "", "ок"]
    assert decode_frames(b"\x00") == []
    with pytest.raises(ValueError):
        encode_frame("x" * 70000)


# ---------- B ----------
def test_b1():
    t = time.perf_counter()
    assert asyncio.run(double_all(list(range(10)))) == [x * 2 for x in range(10)]
    assert time.perf_counter() - t < 0.5, "запросы должны идти конкурентно"


def test_b2():
    t = time.perf_counter()
    assert asyncio.run(first_answer({"Аня": 0.3, "Боря": 0.05, "Вика": 1.0})) == "Боря"
    assert time.perf_counter() - t < 0.25, "остальных ждать не надо"


def test_b3():
    async def fast():
        await asyncio.sleep(0.01)
        return 42

    async def slow():
        await asyncio.sleep(1)
        return 1

    assert asyncio.run(with_timeout(fast(), 0.5)) == 42
    t = time.perf_counter()
    assert asyncio.run(with_timeout(slow(), 0.05)) is None
    assert asyncio.run(with_timeout(slow(), 0.05, default="таймаут")) == "таймаут"
    assert time.perf_counter() - t < 0.5


def test_b4():
    state = {"now": 0, "max": 0}

    def make(i):
        async def job():
            state["now"] += 1
            state["max"] = max(state["max"], state["now"])
            await asyncio.sleep(0.02)
            state["now"] -= 1
            return i * i
        return job

    t = time.perf_counter()
    assert asyncio.run(limited([make(i) for i in range(9)], 3)) == [i * i for i in range(9)]
    assert state["max"] == 3
    assert time.perf_counter() - t < 0.5


# ---------- C ----------
def test_c1():
    assert assign_rooms(list("abcde"), 2) == ([["a", "b"], ["c", "d"]], ["e"])
    assert assign_rooms(list("abcd"), 4) == ([["a", "b", "c", "d"]], [])
    assert assign_rooms([], 2) == ([], [])


def test_c2():
    assert max_online([(1, "in"), (2, "in"), (3, "out"), (3, "in"), (5, "in")]) == 3
    assert max_online([(1, "in"), (2, "out"), (2, "in")]) == 1
    assert max_online([]) == 0


def test_c3():
    assert first_out_of_turn(["Аня", "Боря", "Аня", "Аня"], ["Аня", "Боря"]) == 3
    assert first_out_of_turn(["Боря"], ["Аня", "Боря"]) == 0
    assert first_out_of_turn(["a", "b", "c", "a"], ["a", "b", "c"]) == -1


def test_c4():
    q = [("Аня", 1200), ("Боря", 1500), ("Вика", 1250), ("Гоша", 1480), ("Даня", 900)]
    assert matchmake(q, 100) == [("Аня", "Вика"), ("Боря", "Гоша")]
    assert matchmake(q, 10) == []
    assert matchmake([("a", 1), ("b", 1), ("c", 1)], 0) == [("a", "b")]


# ---------- D ----------
@pytest.fixture
def client():
    app_module.counter["value"] = 0
    app_module.history.clear()
    with TestClient(app_module.app) as c:
        yield c


def test_d1(client):
    with client.websocket_connect("/ws/echo") as ws:
        ws.send_json({"a": [1, 2]})
        assert ws.receive_json() == {"type": "echo", "data": {"a": [1, 2]}}
        ws.send_text("{")
        assert ws.receive_json() == {"type": "error", "code": "bad_json"}
        ws.send_text("5")
        assert ws.receive_json() == {"type": "echo", "data": 5}


def test_d2(client):
    with client.websocket_connect("/ws/counter") as a:
        assert a.receive_json() == {"type": "count", "value": 0}
        with client.websocket_connect("/ws/counter") as b:
            assert b.receive_json() == {"type": "count", "value": 0}
            b.send_json({"type": "inc"})
            assert a.receive_json() == b.receive_json() == {"type": "count", "value": 1}
        a.send_json({"type": "inc"})
        assert a.receive_json() == {"type": "count", "value": 2}


def test_d3(client):
    with client.websocket_connect("/ws/chat/r1?name=Аня") as a:
        assert a.receive_json() == {"type": "history", "messages": []}
        for i in range(7):
            a.send_text(f"m{i}")
            a.receive_json()
        a.send_text("   ")
        with client.websocket_connect("/ws/chat/r1?name=Боря") as b, \
                client.websocket_connect("/ws/chat/r2?name=Вика") as v:
            h = b.receive_json()["messages"]
            assert [m["text"] for m in h] == ["m2", "m3", "m4", "m5", "m6"]
            assert v.receive_json() == {"type": "history", "messages": []}
            b.send_text("привет")
            assert a.receive_json() == b.receive_json() == {"type": "chat", "from": "Боря", "text": "привет"}
            v.send_text("я в другой комнате")
            assert v.receive_json()["text"] == "я в другой комнате"
            b.send_text("ещё")
            assert a.receive_json()["text"] == "ещё"


# ---------- E4 ----------
def fleet(*ships):
    f = Fleet()
    for s in ships:
        f.place(*s)
    return f


def test_e4a():
    f = fleet((0, 0, 4, True), (2, 0, 3, False))
    assert len(f.ships) == 2
    for bad in [(0, 8, 3, True), (9, 0, 2, False), (1, 4, 1, True), (1, 0, 2, True)]:
        with pytest.raises(ValueError):
            f.place(*bad)
    f.place(0, 5, 1, True)            # через клетку от (0, 3) — можно
    assert len(f.ships) == 3


def test_e4b():
    f = fleet((0, 0, 2, True), (5, 5, 1, True))
    assert f.shoot(0, 0) == "hit"
    assert f.shoot(3, 3) == "miss"
    assert f.shoot(0, 1) == "sunk"
    assert f.shoot(5, 5) == "sunk" and f.all_sunk()
    for cell in [(0, 0), (10, 0), (-1, 3)]:
        with pytest.raises(ShotError):
            f.shoot(*cell)
    g = fleet((0, 0, 3, True))
    g.shoot(0, 0); g.shoot(1, 1)
    assert g.view()[:2] == ["x.........", ".o........"]
    g.shoot(0, 1); g.shoot(0, 2)
    assert g.view()[0] == "###......."


def test_e4c():
    b = Battle(fleet((0, 0, 2, True)), fleet((9, 9, 1, True), (0, 0, 1, True)))
    assert b.fire(0, 5, 5) == "miss" and b.turn == 1
    with pytest.raises(ShotError):
        b.fire(0, 1, 1)
    assert b.fire(1, 0, 0) == "hit" and b.turn == 1
    assert b.fire(1, 5, 5) == "miss" and b.turn == 0
    assert b.fire(0, 9, 9) == "sunk" and b.turn == 0
    assert b.fire(0, 0, 0) == "win" and b.winner == 0
    with pytest.raises(ShotError):
        b.fire(1, 0, 1)


# ---------- E5* ----------
def blank():
    return ["." * 10 for _ in range(10)]


def put(view, cells, ch):
    v = [list(r) for r in view]
    for r, c in cells:
        v[r][c] = ch
    return ["".join(r) for r in v]


def test_e5():
    assert next_shot(blank()) == (0, 0)
    assert next_shot(put(blank(), [(0, 0)], "o")) == (0, 2)
    v = put(blank(), [(4, 4)], "x")
    assert next_shot(v) == (3, 4)
    v = put(v, [(3, 4)], "o")
    assert next_shot(v) == (4, 5)
    v = put(blank(), [(4, 4), (4, 5)], "x")
    assert next_shot(v) == (4, 3)
    v = put(v, [(4, 3)], "o")
    assert next_shot(v) == (4, 6)
    v = put(blank(), [(2, 7), (3, 7)], "x")
    assert next_shot(v) == (1, 7)
    full = put(blank(), [(r, c) for r in range(10) for c in range(10) if (r + c) % 2 == 0], "o")
    assert next_shot(full) == (0, 1)
