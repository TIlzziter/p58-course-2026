"""E4 · босс. Мини-JWT на HMAC-SHA256."""
import base64
import binascii
import hashlib
import hmac
import json


def b64e(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def b64d(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def _json(obj: dict) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def _sig(secret: str, signing_input: str) -> str:
    return b64e(hmac.new(secret.encode(), signing_input.encode(), hashlib.sha256).digest())


def encode(payload: dict, secret: str, kid: str = "k1") -> str:
    """а) "<заголовок>.<данные>.<подпись>": base64url без "=", JSON компактный с ключами по алфавиту,
    заголовок {"alg": "HS256", "kid": kid, "typ": "JWT"}, подпись — HMAC-SHA256 от "<заголовок>.<данные>"."""
    h = b64e(_json({"alg": "HS256", "kid": kid, "typ": "JWT"}))
    p = b64e(_json(payload))
    return f"{h}.{p}.{_sig(secret, f'{h}.{p}')}"


def decode(token: str, keys: dict[str, str], now: int, leeway: int = 0) -> dict:
    """б) Проверить и вернуть данные. ValueError с текстом: "format", "alg", "kid", "signature",
    "expired" (now > exp + leeway), "not_yet" (now < nbf − leeway). Проверки в этом порядке."""
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("format")
    try:
        header = json.loads(b64d(parts[0]))
        payload = json.loads(b64d(parts[1]))
    except (ValueError, binascii.Error):
        raise ValueError("format") from None
    if not isinstance(header, dict) or not isinstance(payload, dict):
        raise ValueError("format")
    if header.get("alg") != "HS256":
        raise ValueError("alg")
    secret = keys.get(header.get("kid"))
    if secret is None:
        raise ValueError("kid")
    if not hmac.compare_digest(_sig(secret, f"{parts[0]}.{parts[1]}"), parts[2]):
        raise ValueError("signature")
    if "exp" in payload and now > payload["exp"] + leeway:
        raise ValueError("expired")
    if "nbf" in payload and now < payload["nbf"] - leeway:
        raise ValueError("not_yet")
    return payload


def refresh(token: str, keys: dict[str, str], current_kid: str, now: int, ttl: int, max_age: int) -> str:
    """в) Обновить токен: decode (истёкший по exp — тоже ошибка), нет iat — ValueError("iat"),
    now − iat > max_age — ValueError("too_old"). Новый токен: те же данные, iat = now, exp = now + ttl,
    подписан ключом current_kid."""
    payload = decode(token, keys, now)
    if "iat" not in payload:
        raise ValueError("iat")
    if now - payload["iat"] > max_age:
        raise ValueError("too_old")
    return encode(payload | {"iat": now, "exp": now + ttl}, keys[current_kid], current_kid)
