"""Задачи 1–2. Ограничение частоты запросов."""
import time
from collections import deque
from collections.abc import Callable


class TokenBucket:
    """Ведро токенов: `rate` токенов в секунду, не больше `capacity`. В начале ведро полное.

    allow(cost) — если токенов хватает, списать и вернуть True, иначе False (ничего не списывать).
    retry_after(cost) — через сколько секунд хватит токенов (0.0, если уже хватает).
    cost больше capacity — ValueError (такой запрос не пройдёт никогда).
    """

    def __init__(self, rate: float, capacity: int, now: Callable[[], float] = time.monotonic):
        self.rate = rate
        self.capacity = capacity
        self.now = now
        self.tokens = float(capacity)
        self.last = now()

    def allow(self, cost: float = 1) -> bool:
        # TODO: пополнить ведро по прошедшему времени (не больше capacity), проверить cost
        t = self.now()
        self.tokens += (t - self.last) * self.rate
        self.last = t
        self.tokens -= cost
        return self.tokens >= 0

    def retry_after(self, cost: float = 1) -> float:
        raise NotImplementedError


class KeyedLimiter:
    """Скользящее окно для каждого ключа: не больше `limit` разрешённых событий за `window` секунд.

    Событие в момент t учитывает разрешённые события из (t − window, t]. Отклонённые не считаются.
    hit(key) -> (разрешено, через сколько секунд можно снова: 0.0 при разрешении).
    cleanup() удаляет ключи без событий в окне; len(limiter) — сколько ключей хранится.
    """

    def __init__(self, limit: int, window: float, now: Callable[[], float] = time.monotonic):
        self.limit = limit
        self.window = window
        self.now = now
        self.log: dict[str, deque[float]] = {}

    def hit(self, key: str) -> tuple[bool, float]:
        # TODO: убирать старые события, не записывать отклонённые, считать retry_after
        q = self.log.setdefault(key, deque())
        q.append(self.now())
        return len(q) <= self.limit, 0.0

    def cleanup(self) -> None:
        raise NotImplementedError

    def __len__(self) -> int:
        return len(self.log)
