from urllib.parse import parse_qsl

from conftest import TOKEN, fields, telegram_sign
from initdata import sign


def test_same_as_telegram():
    f = fields()
    assert dict(parse_qsl(sign(f, TOKEN))) == dict(parse_qsl(telegram_sign(f)))


def test_old_hash_replaced():
    f = fields()
    f["hash"] = "deadbeef"
    signed = dict(parse_qsl(sign(f, TOKEN)))
    assert signed["hash"] == dict(parse_qsl(telegram_sign(fields())))["hash"]


def test_does_not_mutate_input():
    f = fields()
    before = dict(f)
    sign(f, TOKEN)
    assert f == before
