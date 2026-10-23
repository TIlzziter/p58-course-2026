"""Протокол сообщений комнаты.

Клиент → сервер:
    {"type": "move", "col": 0..6}
    {"type": "chat", "text": "..."}      — 1..200 символов после strip()
    {"type": "ping"}
Лишних ключей быть не должно. Ошибки — ProtocolError с кодом bad_json, bad_type или bad_field.
"""
import json

MAX_CHAT = 200


class ProtocolError(ValueError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def parse_message(raw: str) -> dict:
    """Задача 1. Строка от клиента → проверенный словарь."""
    msg = json.loads(raw)                       # агент: «JSON всегда корректный»
    if msg["type"] == "move":
        if not isinstance(msg.get("col"), int) or not 0 <= msg["col"] <= 6:
            raise ProtocolError("bad_field")
        return msg
    if msg["type"] == "chat":
        return msg
    if msg["type"] == "ping":
        return msg
    raise ProtocolError("bad_type")


def error(code: str) -> dict:
    return {"type": "error", "code": code}
