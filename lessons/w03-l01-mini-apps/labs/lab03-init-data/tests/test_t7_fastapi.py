import pytest
from fastapi.testclient import TestClient

import initdata
from conftest import NOW, fields, telegram_sign


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setitem(initdata.CLOCK, "now", NOW)
    return TestClient(initdata.app)


def test_me(client, good):
    r = client.get("/me", headers={"Authorization": f"tma {good}"})
    assert r.status_code == 200
    assert r.json() == {"id": 42, "first_name": "Аня", "username": "anya_p58"}


@pytest.mark.parametrize("headers,code", [
    ({}, "no_init_data"),
    ({"Authorization": "Bearer abc"}, "no_init_data"),
    ({"Authorization": "tma user=1&hash=00"}, "bad_hash"),
])
def test_rejects(client, headers, code):
    r = client.get("/me", headers=headers)
    assert r.status_code == 401
    assert r.json()["detail"]["code"] == code


def test_expired_401(client):
    raw = telegram_sign(fields(auth_date=str(NOW - 100000)))
    r = client.get("/me", headers={"Authorization": f"tma {raw}"})
    assert r.status_code == 401 and r.json()["detail"]["code"] == "expired"
