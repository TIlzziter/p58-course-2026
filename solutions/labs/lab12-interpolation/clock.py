"""Задача 4. Синхронизация часов клиента с сервером."""
from collections import deque


class ClockSync:
    def __init__(self, keep: int = 8):
        self.samples: deque[tuple[float, float]] = deque(maxlen=keep)   # (rtt, offset)

    def add(self, sent: float, server: float, received: float) -> None:
        if received < sent:
            raise ValueError("ответ раньше запроса")
        rtt = received - sent
        self.samples.append((rtt, server - (sent + received) / 2))

    @property
    def offset(self) -> float:
        """Смещение по замеру с наименьшим RTT среди последних keep (при равенстве — более свежий)."""
        if not self.samples:
            raise LookupError("нет замеров")
        best = min(range(len(self.samples)), key=lambda i: (self.samples[i][0], -i))
        return self.samples[best][1]

    @property
    def rtt(self) -> float:
        return min(r for r, _ in self.samples)

    def server_now(self, client_now: float) -> float:
        return client_now + self.offset
