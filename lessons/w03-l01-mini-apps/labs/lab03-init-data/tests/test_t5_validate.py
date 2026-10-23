import pytest
from conftest import NOW, TOKEN, fields, telegram_sign
from initdata import InitDataError, WebAppUser, validate


def test_returns_user(good):
    assert validate(good, TOKEN, NOW) == WebAppUser(id=42, first_name="Аня", username="anya_p58", language_code="ru")


def test_user_without_optional_fields():
    raw = telegram_sign(fields(user='{"id":7,"first_name":"Боря"}'))
    assert validate(raw, TOKEN, NOW) == WebAppUser(id=7, first_name="Боря")


def code(raw, now=NOW, token=TOKEN, **kw):
    with pytest.raises(InitDataError) as e:
        validate(raw, token, now, **kw)
    return e.value.code


def test_bad_hash(good):
    assert code(good, token="1:X") == "bad_hash"


def test_expired():
    raw = telegram_sign(fields(auth_date=str(NOW - 86401)))
    assert code(raw) == "expired"
    assert validate(raw, TOKEN, NOW, max_age=100000).id == 42


def test_from_future():
    assert code(telegram_sign(fields(auth_date=str(NOW + 3600)))) == "expired"


def test_no_auth_date():
    assert code(telegram_sign(fields(auth_date=None))) == "expired"


@pytest.mark.parametrize("user", [None, "not json", '{"first_name":"X"}', "[1,2]"])
def test_no_user(user):
    assert code(telegram_sign(fields(user=user))) == "no_user"
