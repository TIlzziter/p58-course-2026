import pytest
from fastapi.testclient import TestClient

import app as app_module
from tasks import (can_merge, conflict_files, done_percent, free_roles, game_commits, issue_number,
                   parse_story, split_teams, top_authors, validate_move)


def test_a1():
    assert issue_number("feature/12-board") == 12
    assert issue_number("fix/3-bot-crash") == 3
    assert issue_number("main") is None
    assert issue_number("feature/board") is None


def test_a2():
    msgs = ["game: поле 6×7", "Merge pull request #3", "bot: /start", "game: ход", "--", "game: сюда не дойдём"]
    assert game_commits(msgs) == ["game: поле 6×7", "game: ход"]


@pytest.mark.parametrize("v,exp", [(["changes", "approve"], True), (["approve", "changes"], False),
                                   (["approve"], True), ([], False), (["changes"], False),
                                   (["approve", "changes", "changes", "approve"], True)])
def test_a3(v, exp):
    assert can_merge(v) is exp


def test_b1():
    assert top_authors(["Маша", "Петя", "Маша", "Аня", "Петя", "Маша"]) == [("Маша", 3), ("Петя", 2), ("Аня", 1)]
    assert top_authors(["Б", "А"]) == [("А", 1), ("Б", 1)]


def test_b2():
    s = {"Аня": ("бэкенд", "devops"), "Петя": ("фронтенд", "дизайн"), "Маша": ("бэкенд", "аналитика")}
    assert free_roles(s) == {"аналитика", "тестирование", "devops", "дизайн"}


def test_b3():
    assert conflict_files(["bot/main.py", "api/rooms.py", "README.md"],
                          ["api/rooms.py", "web/app.js", "README.md"]) == ["README.md", "api/rooms.py"]


def test_b4():
    assert split_teams([10, 20, 30, 40, 50, 60, 70, 80]) == 0
    assert split_teams([1, 1, 1, 1, 1, 1, 1, 100]) == 99
    assert split_teams([5, 5, 5, 5, 6, 6, 6, 7]) == 1


def test_c1():
    assert done_percent("Задача\n- [x] падает вниз\n- [ ] полный столбец\n- [x] тесты") == 67
    assert done_percent("нет чекбоксов") is None
    assert done_percent("- [ ] a\n- [ ] b") == 0


def test_c2():
    assert parse_story("Как игрок, я хочу пригласить друга, чтобы сыграть вдвоём") == {
        "role": "игрок", "want": "пригласить друга", "why": "сыграть вдвоём"}
    assert parse_story("Хочу кнопку") is None


def test_c3():
    assert validate_move({"type": "move", "col": 3}) == []
    assert validate_move({"type": "move", "col": "3", "cheat": 1}) == ["col должен быть целым числом", "лишние ключи: cheat"]
    assert validate_move({"type": "move", "col": True}) == ["col должен быть целым числом"]
    assert validate_move({"type": "move", "col": 7}) == ["col вне диапазона 0..6"]
    assert validate_move([1]) != []


@pytest.fixture
def client():
    app_module.ISSUES.clear()
    return TestClient(app_module.app)


def test_e1(client):
    assert client.get("/ping").json() == {"pong": True}
    assert client.get("/rooms/abc").json() == {"id": "abc", "players": ["Аня"]}
    assert client.get("/rooms/zzz").status_code == 404


def test_e4_a(client):
    r = client.post("/issues", json={"title": "Поле 6×7"})
    assert r.status_code == 201 and r.json() == {"id": 1, "title": "Поле 6×7", "status": "backlog"}
    client.post("/issues", json={"title": "Бот"})
    client.post("/issues/2/move", json={"to": "todo"})
    assert [i["id"] for i in client.get("/issues", params={"status": "todo"}).json()] == [2]
    assert len(client.get("/issues").json()) == 2


def test_e4_b(client):
    client.post("/issues", json={"title": "x"})
    r = client.post("/issues/1/move", json={"to": "done"})
    assert r.status_code == 409 and r.json()["detail"] == "Нельзя перейти из backlog в done"
    for to in ["todo", "in_progress", "review", "in_progress", "review", "done"]:
        assert client.post("/issues/1/move", json={"to": to}).status_code == 200
    assert client.post("/issues/9/move", json={"to": "todo"}).status_code == 404


def test_e4_c(client):
    assert client.get("/board").json()["done_percent"] == 0
    client.post("/issues", json={"title": "x"})
    assert client.get("/board").json() == {"backlog": [1], "todo": [], "in_progress": [], "review": [], "done": [],
                                           "done_percent": 0}
    client.post("/issues", json={"title": "y"})
    for to in ["todo", "in_progress", "review", "done"]:
        client.post("/issues/2/move", json={"to": to})
    assert client.get("/board").json()["done_percent"] == 50
