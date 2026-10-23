import pytest
from app import create_app
from fastapi.testclient import TestClient


@pytest.fixture
def client(clock):
    return TestClient(create_app(limit=3, window=60, now=clock))


def post(client, score=10, user="ann"):
    return client.post("/api/score", json={"score": score}, headers={"X-User-Id": user})


def test_limit_and_retry_after(client, clock):
    assert [post(client).status_code for _ in range(3)] == [200, 200, 200]
    r = post(client)
    assert r.status_code == 429
    assert r.json() == {"error": "rate_limited"}
    assert r.headers["Retry-After"] == "60"
    clock.tick(59.5)
    r = post(client)
    assert r.status_code == 429 and r.headers["Retry-After"] == "1"
    clock.tick(0.5)
    assert post(client).json() == {"saved": 10}


def test_per_user_and_health(client):
    for _ in range(3):
        post(client, user="ann")
    assert post(client, user="ann").status_code == 429
    assert post(client, user="bob").status_code == 200
    assert all(client.get("/health").status_code == 200 for _ in range(10))


def test_score_validation(client):
    assert post(client, score=-1).status_code == 422
    assert post(client, score=10_001).status_code == 422
    assert post(client, score=10_000).json() == {"saved": 10_000}


def test_no_header_uses_ip(client):
    for _ in range(3):
        assert client.post("/api/score", json={"score": 1}).status_code == 200
    assert client.post("/api/score", json={"score": 1}).status_code == 429
