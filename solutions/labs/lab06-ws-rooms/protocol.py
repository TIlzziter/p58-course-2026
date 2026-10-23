"""Протокол сообщений комнаты (эталон)."""
import json

MAX_CHAT = 200


class ProtocolError(ValueError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


FIELDS = {"move": {"col"}, "chat": {"text"}, "ping": set()}


def parse_message(raw: str) -> dict:
    """Строка от клиента → проверенный словарь. Ошибки: bad_json, bad_type, bad_field."""
    try:
        msg = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        raise ProtocolError("bad_json") from None
    if not isinstance(msg, dict) or msg.get("type") not in FIELDS:
        raise ProtocolError("bad_type")
    kind = msg["type"]
    if set(msg) - {"type"} != FIELDS[kind]:
        raise ProtocolError("bad_field")
    if kind == "move":
        col = msg["col"]
        if type(col) is not int or not 0 <= col <= 6:
            raise ProtocolError("bad_field")
        return {"type": "move", "col": col}
    if kind == "chat":
        text = msg["text"]
        if not isinstance(text, str) or not text.strip() or len(text.strip()) > MAX_CHAT:
            raise ProtocolError("bad_field")
        return {"type": "chat", "text": text.strip()}
    return {"type": "ping"}


def error(code: str) -> dict:
    return {"type": "error", "code": code}
