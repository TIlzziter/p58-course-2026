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

    def _refill(self) -> None:
        t = self.now()
        self.tokens = min(self.capacity, self.tokens + (t - self.last) * self.rate)
        self.last = t

    def _check(self, cost: float) -> None:
        if cost > self.capacity:
            raise ValueError("cost больше ёмкости ведра")

    def allow(self, cost: float = 1) -> bool:
        self._check(cost)
        self._refill()
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False

    def retry_after(self, cost: float = 1) -> float:
        self._check(cost)
        self._refill()
        return max(0.0, (cost - self.tokens) / self.rate)


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

    def _trim(self, q: deque[float], t: float) -> None:
        while q and q[0] <= t - self.window:
            q.popleft()

    def hit(self, key: str) -> tuple[bool, float]:
        t = self.now()
        q = self.log.setdefault(key, deque())
        self._trim(q, t)
        if len(q) < self.limit:
            q.append(t)
            return True, 0.0
        return False, q[0] + self.window - t

    def cleanup(self) -> None:
        t = self.now()
        for key in list(self.log):
            self._trim(self.log[key], t)
            if not self.log[key]:
                del self.log[key]

    def __len__(self) -> int:
        return len(self.log)
