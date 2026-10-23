"""Задача 2. Разбор ответа модели: JSON со схемой."""
import json
import re

from pydantic import BaseModel, Field, ValidationError  # noqa: F401

FENCE = re.compile(r"```(?:json)?\s*\n(.*?)```", re.DOTALL)


class Hint(BaseModel):
    hint: str = Field(min_length=1, max_length=200)
    confidence: float = Field(ge=0, le=1)


def parse_answer(text: str) -> Hint | None:
    """Модель просили ответить JSON {"hint": строка 1..200, "confidence": 0..1}. Она может добавить текст
    до и после или обернуть JSON в ```json … ```. Если есть блок ``` — берём первый такой блок, иначе —
    от первой "{" до последней "}". Не JSON, не объект, не по схеме — None (без исключений)."""
    # TODO: блок ```json, текст вокруг JSON, ошибки схемы -> None
    try:
        return Hint.model_validate(json.loads(text))
    except json.JSONDecodeError:
        return None
