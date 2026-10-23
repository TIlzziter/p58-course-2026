import pytest


@pytest.mark.parametrize("payload", [{}, {"player": ""}, {"name": "аня"}])
def test_validation_error_format(client, payload):
    r = client.post("/rooms", json=payload)
    assert r.status_code == 422
    detail = r.json()["detail"]
    assert isinstance(detail, dict), "detail должен быть объектом, а не списком FastAPI"
    assert detail["code"] == "validation_error"
    assert isinstance(detail["message"], str) and detail["message"]


def test_query_validation_format(client):
    r = client.get("/rooms", params={"status": "lost"})
    assert r.status_code == 422
    assert r.json()["detail"]["code"] == "validation_error"


def test_messages_are_human(client):
    r = client.get("/rooms/7")
    msg = r.json()["detail"]["message"]
    assert "Traceback" not in msg and "KeyError" not in msg
    assert any("а" <= ch <= "я" for ch in msg.lower()), "сообщение для человека — по-русски"
