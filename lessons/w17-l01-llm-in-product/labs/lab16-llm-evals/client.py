"""Задача 4. Клиент модели: повторы, кэш, бюджет токенов.

transport(messages) — функция, которая ходит в API модели. Возвращает словарь
{"status": int, "text": str, "usage": {"in": int, "out": int}, "retry_after": float | None}
или бросает TimeoutError. В тестах вместо сети — подменный transport, вместо time.sleep — запись пауз.
"""
import json  # noqa: F401
import time

RETRY_STATUS = {429, 500, 502, 503}


class LLMError(Exception):
    pass


class BudgetExceeded(LLMError):
    pass


class LLMClient:
    """complete(messages) -> текст ответа.

    * Кэш: одинаковые messages (сравниваем json.dumps(messages, sort_keys=True)) — ответ из кэша,
      transport не вызываем, токены не тратим.
    * Бюджет: если уже потрачено токенов (in + out) не меньше budget — BudgetExceeded до запроса.
    * Повторы: статусы RETRY_STATUS и TimeoutError — пауза и повтор, всего попыток 1 + max_retries.
      Пауза — retry_after из ответа, если он есть, иначе base_delay · 2^номер_повтора (0, 1, 2, …).
      После последней неудачи — LLMError. Другой статус не 200 (например, 400) — LLMError сразу.
    * spent — потрачено токенов, calls — сколько раз вызвали transport.
    """

    def __init__(self, transport, sleep=time.sleep, max_retries: int = 3, base_delay: float = 0.5,
                 budget: int = 100_000):
        self.transport = transport
        self.sleep = sleep
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.budget = budget
        self.spent = 0
        self.calls = 0
        self.cache: dict[str, str] = {}

    def complete(self, messages: list[dict]) -> str:
        # TODO: кэш, бюджет, повторы с паузами, LLMError
        self.calls += 1
        resp = self.transport(messages)
        self.spent += resp["usage"]["in"] + resp["usage"]["out"]
        return resp["text"]
