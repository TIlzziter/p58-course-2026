"""Задача 4. Клиент модели: повторы, кэш, бюджет токенов.

transport(messages) — функция, которая ходит в API модели. Возвращает словарь
{"status": int, "text": str, "usage": {"in": int, "out": int}, "retry_after": float | None}
или бросает TimeoutError. В тестах вместо сети — подменный transport, вместо time.sleep — запись пауз.
"""
import json
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
        key = json.dumps(messages, sort_keys=True, ensure_ascii=False)
        if key in self.cache:
            return self.cache[key]
        if self.spent >= self.budget:
            raise BudgetExceeded(f"потрачено {self.spent} из {self.budget}")
        for attempt in range(self.max_retries + 1):
            self.calls += 1
            retry_after = None
            try:
                resp = self.transport(messages)
            except TimeoutError:
                resp = None
            if resp is not None:
                usage = resp.get("usage") or {}
                self.spent += usage.get("in", 0) + usage.get("out", 0)
                if resp["status"] == 200:
                    self.cache[key] = resp["text"]
                    return resp["text"]
                if resp["status"] not in RETRY_STATUS:
                    raise LLMError(f"статус {resp['status']}")
                retry_after = resp.get("retry_after")
            if attempt == self.max_retries:
                break
            self.sleep(retry_after if retry_after is not None else self.base_delay * 2 ** attempt)
        raise LLMError("попытки кончились")
