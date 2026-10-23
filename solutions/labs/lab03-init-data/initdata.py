"""Проверка initData Telegram Mini App (эталон).

Алгоритм из документации Telegram (core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app):
1. data_check_string — все поля, кроме hash, в виде key=value, отсортированные по ключу, через "\\n";
2. secret_key = HMAC_SHA256(key="WebAppData", msg=bot_token);
3. hash должен совпасть с hex(HMAC_SHA256(key=secret_key, msg=data_check_string)).
"""
import hashlib
import hmac
import json
from dataclasses import dataclass
from urllib.parse import parse_qsl, urlencode

from fastapi import Depends, FastAPI, Header, HTTPException


class InitDataError(Exception):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class WebAppUser:
    id: int
    first_name: str
    username: str | None = None
    language_code: str | None = None


def parse_init_data(raw: str) -> dict[str, str]:
    """Строка запроса → словарь. Значения декодированы. Повтор ключа или мусор — InitDataError("malformed")."""
    try:
        pairs = parse_qsl(raw, keep_blank_values=True, strict_parsing=True)
    except ValueError:
        raise InitDataError("malformed") from None
    fields: dict[str, str] = {}
    for k, v in pairs:
        if k in fields:
            raise InitDataError("malformed")
        fields[k] = v
    return fields


def data_check_string(fields: dict[str, str]) -> str:
    return "\n".join(f"{k}={fields[k]}" for k in sorted(fields) if k != "hash")


def secret_key(bot_token: str) -> bytes:
    return hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()


def compute_hash(fields: dict[str, str], bot_token: str) -> str:
    return hmac.new(secret_key(bot_token), data_check_string(fields).encode(), hashlib.sha256).hexdigest()


def sign(fields: dict[str, str], bot_token: str) -> str:
    """Подписать поля (так делает Telegram) — нужно для тестов и локальной отладки."""
    fields = {k: v for k, v in fields.items() if k != "hash"}
    return urlencode({**fields, "hash": compute_hash(fields, bot_token)})


def verify(raw: str, bot_token: str) -> bool:
    try:
        fields = parse_init_data(raw)
    except InitDataError:
        return False
    received = fields.get("hash")
    if not received:
        return False
    return hmac.compare_digest(received, compute_hash(fields, bot_token))


def validate(raw: str, bot_token: str, now: int, max_age: int = 86400) -> WebAppUser:
    """Проверить подпись и свежесть, вернуть пользователя. Ошибки: bad_hash, expired, no_user."""
    if not verify(raw, bot_token):
        raise InitDataError("bad_hash")
    fields = parse_init_data(raw)
    try:
        auth_date = int(fields["auth_date"])
    except (KeyError, ValueError):
        raise InitDataError("expired") from None
    if not 0 <= now - auth_date <= max_age:
        raise InitDataError("expired")
    try:
        u = json.loads(fields["user"])
        return WebAppUser(id=int(u["id"]), first_name=u["first_name"],
                          username=u.get("username"), language_code=u.get("language_code"))
    except (KeyError, ValueError, TypeError):
        raise InitDataError("no_user") from None


# ---- задача 7*: FastAPI ----
BOT_TOKEN = "123456:TEST-TOKEN-for-lab03"
CLOCK = {"now": 1_760_000_000}       # в тестах время подменяется; в проде — int(time.time())
app = FastAPI()


def current_user(authorization: str | None = Header(default=None)) -> WebAppUser:
    if not authorization or not authorization.startswith("tma "):
        raise HTTPException(401, detail={"code": "no_init_data", "message": "Нет заголовка Authorization: tma ..."})
    try:
        return validate(authorization[4:], BOT_TOKEN, CLOCK["now"])
    except InitDataError as e:
        raise HTTPException(401, detail={"code": e.code, "message": "initData не прошла проверку"}) from None


@app.get("/me")
def me(user: WebAppUser = Depends(current_user)) -> dict:
    return {"id": user.id, "first_name": user.first_name, "username": user.username}
