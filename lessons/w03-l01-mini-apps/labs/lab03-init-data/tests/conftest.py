"""Независимая подпись initData «как в Telegram» — тесты не зависят от вашего кода."""
import hashlib
import hmac
import json
from urllib.parse import urlencode

import pytest

TOKEN = "123456:TEST-TOKEN-for-lab03"
NOW = 1_760_000_000
USER = {"id": 42, "first_name": "Аня", "username": "anya_p58", "language_code": "ru"}


def telegram_sign(fields: dict, token: str = TOKEN) -> str:
    dcs = "\n".join(f"{k}={fields[k]}" for k in sorted(fields))
    key = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    h = hmac.new(key, dcs.encode(), hashlib.sha256).hexdigest()
    return urlencode({**fields, "hash": h})


def fields(**over) -> dict:
    base = {"query_id": "AAHdF6IQAAAAAN0XohDhrOrc", "user": json.dumps(USER, ensure_ascii=False, separators=(",", ":")),
            "auth_date": str(NOW - 60)}
    base.update(over)
    return {k: v for k, v in base.items() if v is not None}


@pytest.fixture
def good():
    return telegram_sign(fields())
