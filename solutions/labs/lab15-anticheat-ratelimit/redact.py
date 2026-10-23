"""Задача 5. Вычищаем секреты и личные данные перед записью в лог или отправкой агенту."""
import re
from typing import Any

SECRET_KEYS = {"password", "token", "secret", "api_key", "authorization", "init_data"}

BOT_TOKEN = re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{35}\b")
BEARER = re.compile(r"\bBearer\s+[^\s\"',]+", re.IGNORECASE)
EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b")
PHONE = re.compile(r"\+\d(?:[ ()-]*\d){9,12}")
KEY_VALUE = re.compile(r"(?i)\b(" + "|".join(sorted(SECRET_KEYS)) + r")=([^\s&]+)")
JSON_PAIR = re.compile(r'(?i)("(?:' + "|".join(sorted(SECRET_KEYS)) + r')"\s*:\s*)"[^"]*"')


def redact(text: str) -> str:
    """Заменить в строке:
      токен бота `123456789:AA…` (8–10 цифр, двоеточие, 35 символов [A-Za-z0-9_-]) → "[BOT_TOKEN]";
      `Bearer <что угодно до пробела>` → "Bearer ***";
      `ключ=значение` и `"ключ": "значение"` для ключей из SECRET_KEYS (без учёта регистра) → значение "***";
      e-mail → "[EMAIL]"; телефон: «+», затем 10–13 цифр, между ними пробелы, скобки, дефисы → "[PHONE]".
    Остальной текст не трогаем.
    """
    text = BOT_TOKEN.sub("[BOT_TOKEN]", text)
    text = BEARER.sub("Bearer ***", text)
    text = KEY_VALUE.sub(lambda m: f"{m.group(1)}=***", text)
    text = JSON_PAIR.sub(lambda m: f'{m.group(1)}"***"', text)
    text = EMAIL.sub("[EMAIL]", text)
    return PHONE.sub("[PHONE]", text)


def redact_record(value: Any) -> Any:
    """То же для записи лога: словари и списки — рекурсивно (новый объект, исходный не меняем);
    значение под ключом из SECRET_KEYS (без учёта регистра) → "***" целиком; строки — через redact;
    числа и прочее — как есть."""
    if isinstance(value, dict):
        return {k: "***" if isinstance(k, str) and k.lower() in SECRET_KEYS else redact_record(v)
                for k, v in value.items()}
    if isinstance(value, list | tuple):
        return type(value)(redact_record(v) for v in value)
    if isinstance(value, str):
        return redact(value)
    return value
