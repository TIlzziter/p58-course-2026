"""Задача 7*. Сводка инцидента по логам запросов."""


def incident_summary(records: list[dict], ratio: float = 0.1, min_requests: int = 5) -> dict | None:
    """Минута — [k·60, k·60 + 60). «Плохая» минута: запросов ≥ min_requests и доля 5xx > ratio.
    Инцидент — от начала первой до конца последней плохой минуты.
    Ответ: {"start", "end", "errors" (5xx внутри), "top_path" (чаще всех среди 5xx, ничья — по имени),
    "bad_minutes"}. Плохих нет — None."""
    raise NotImplementedError
