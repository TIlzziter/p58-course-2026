import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.pool import NullPool

from models import Base


@pytest.fixture
def client(tmp_path):
    import app as app_module
    from sqlalchemy.ext.asyncio import create_async_engine

    path = tmp_path / "api.db"
    sync = create_engine(f"sqlite:///{path}")
    Base.metadata.create_all(sync)
    sync.dispose()
    eng = create_async_engine(f"sqlite+aiosqlite:///{path}", poolclass=NullPool)
    maker = async_sessionmaker(eng, expire_on_commit=False)

    async def override():
        async with maker() as s:
            yield s

    app_module.app.dependency_overrides[app_module.get_session] = override
    with TestClient(app_module.app) as c:
        yield c
    app_module.app.dependency_overrides.clear()


def match(r="win1", a=(1, "Аня"), b=(2, "Боря")):
    return {"game": "c4", "player1": {"tg_id": a[0], "name": a[1]},
            "player2": {"tg_id": b[0], "name": b[1]}, "result": r}


def test_flow(client):
    r = client.post("/matches", json=match())
    assert r.status_code == 201
    assert r.json()["delta1"] == 16 and r.json()["delta2"] == -16
    client.post("/matches", json=match("draw", b=(3, "Вика")))
    assert client.get("/leaderboard").json() == [
        {"name": "Аня", "rating": 1015, "games": 2},
        {"name": "Вика", "rating": 1001, "games": 1},
        {"name": "Боря", "rating": 984, "games": 1},
    ]
    h = client.get("/players/2/history").json()
    assert h == [{"game": "c4", "opponent": "Аня", "result": "loss", "delta": -16}]


def test_errors(client):
    assert client.post("/matches", json=match("lose")).status_code == 422
    assert client.post("/matches", json=match(b=(1, "Аня"))).status_code == 400
    assert client.get("/players/5/history").status_code == 404
    assert client.get("/leaderboard").json() == []
