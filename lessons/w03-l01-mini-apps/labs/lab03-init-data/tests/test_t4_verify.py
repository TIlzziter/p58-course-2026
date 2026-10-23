import hmac

import pytest
from conftest import TOKEN, fields, telegram_sign
from initdata import verify


def test_good(good):
    assert verify(good, TOKEN)


def test_wrong_token(good):
    assert not verify(good, "999:OTHER")


def test_tampered_user():
    raw = telegram_sign(fields())
    forged = raw.replace("%22id%22%3A42", "%22id%22%3A1")   # подменили id
    assert forged != raw
    assert not verify(forged, TOKEN)


@pytest.mark.parametrize("raw", ["user=%7B%7D&auth_date=1", "abc", "", "a=1&a=1&hash=00"])
def test_no_hash_or_garbage_is_false(raw):
    assert verify(raw, TOKEN) is False


def test_uses_constant_time_compare(good, monkeypatch):
    calls = []
    real = hmac.compare_digest

    def spy(a, b):
        calls.append(1)
        return real(a, b)

    monkeypatch.setattr(hmac, "compare_digest", spy)
    assert verify(good, TOKEN)
    assert calls, "сравнивайте подписи через hmac.compare_digest"
