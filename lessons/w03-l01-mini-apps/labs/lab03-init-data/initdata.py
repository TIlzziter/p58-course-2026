"""Проверка initData Telegram Mini App.

Когда Telegram открывает Mini App, странице доступна строка Telegram.WebApp.initData, например:
    query_id=AAH...&user=%7B%22id%22%3A42%2C%22first_name%22%3A%22%D0%90%D0%BD%D1%8F%22%7D&auth_date=1760000000&hash=ab12...
Клиент пересылает её серверу, а сервер ОБЯЗАН проверить подпись: иначе кто угодно подставит чужой id.

Алгоритм (core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app):
1. data_check_string — все поля, кроме hash, в виде key=value, отсортированные по ключу, через "\\n";
2. secret_key = HMAC_SHA256(key="WebAppData", msg=bot_token);
3. hash должен совпасть с hex(HMAC_SHA256(key=secret_key, msg=data_check_string)).

Каркас написал агент; в нём ошибки. Задачи — в README.md.
"""
import hashlib
import hmac
import json  # noqa: F401
from dataclasses import dataclass

from fastapi import Depends, FastAPI, Header, HTTPException  # noqa: F401


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
    fields = {}
    for pair in raw.split("&"):
        k, v = pair.split("=")
        fields[k] = v
    return fields


def data_check_string(fields: dict[str, str]) -> str:
    return "&".join(f"{k}={fields[k]}" for k in sorted(fields))


def secret_key(bot_token: str) -> bytes:
    return hmac.new(bot_token.encode(), b"WebAppData", hashlib.sha256).digest()


def compute_hash(fields: dict[str, str], bot_token: str) -> str:
    return hmac.new(secret_key(bot_token), data_check_string(fields).encode(), hashlib.sha256).hexdigest()


def sign(fields: dict[str, str], bot_token: str) -> str:
    """Подписать поля (так делает Telegram) — нужно для тестов и локальной отладки. Вернуть строку запроса с hash."""
    raise NotImplementedError("задача 6")


def verify(raw: str, bot_token: str) -> bool:
    fields = parse_init_data(raw)
    return fields["hash"] == compute_hash(fields, bot_token)


def validate(raw: str, bot_token: str, now: int, max_age: int = 86400) -> WebAppUser:
    """Проверить подпись и свежесть, вернуть пользователя. Ошибки: bad_hash, expired, no_user."""
    raise NotImplementedError("задача 5")


# ---- задача 7*: FastAPI ----
BOT_TOKEN = "123456:TEST-TOKEN-for-lab03"
CLOCK = {"now": 1_760_000_000}       # в тестах время подменяется; в проде — int(time.time())
app = FastAPI()


def current_user(authorization: str | None = Header(default=None)) -> WebAppUser:
    raise NotImplementedError("задача 7")


@app.get("/me")
def me(user: WebAppUser = Depends(current_user)) -> dict:
    return {"id": user.id, "first_name": user.first_name, "username": user.username}
