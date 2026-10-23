"""Задача 2. Разбор ответа модели: JSON со схемой."""
import json
import re

from pydantic import BaseModel, Field, ValidationError

FENCE = re.compile(r"```(?:json)?\s*\n(.*?)```", re.DOTALL)


class Hint(BaseModel):
    hint: str = Field(min_length=1, max_length=200)
    confidence: float = Field(ge=0, le=1)


def parse_answer(text: str) -> Hint | None:
    """Модель просили ответить JSON {"hint": строка 1..200, "confidence": 0..1}. Она может добавить текст
    до и после или обернуть JSON в ```json … ```. Если есть блок ``` — берём первый такой блок, иначе —
    от первой "{" до последней "}". Не JSON, не объект, не по схеме — None (без исключений)."""
    m = FENCE.search(text)
    if m:
        chunk = m.group(1)
    else:
        a, b = text.find("{"), text.rfind("}")
        if a == -1 or b < a:
            return None
        chunk = text[a:b + 1]
    try:
        data = json.loads(chunk)
        if not isinstance(data, dict):
            return None
        return Hint.model_validate(data)
    except (json.JSONDecodeError, ValidationError):
        return None
