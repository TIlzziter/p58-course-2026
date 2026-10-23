"""Задача 6. Игровой цикл с фиксированным шагом и буфером ввода."""
from collections import deque
from collections.abc import Callable


class GameLoop:
    def __init__(self, tick_ms: int, max_catchup: int = 5, buffer: int = 2):
        self.tick_ms, self.max_catchup, self.buffer = tick_ms, max_catchup, buffer
        self.acc = 0.0
        self.queues: dict[str, deque[str]] = {}
        self.dropped = 0

    def push_input(self, name: str, direction: str) -> None:
        q = self.queues.setdefault(name, deque())
        if q and q[-1] == direction:
            return
        if len(q) >= self.buffer:
            q.popleft()
        q.append(direction)

    def take_inputs(self) -> dict[str, str]:
        out = {}
        for name, q in self.queues.items():
            if q:
                out[name] = q.popleft()
        return out

    def advance(self, elapsed_ms: float, on_tick: Callable[[dict[str, str]], None]) -> int:
        self.acc += elapsed_ms
        n = 0
        while self.acc >= self.tick_ms and n < self.max_catchup:
            on_tick(self.take_inputs())
            self.acc -= self.tick_ms
            n += 1
        if self.acc >= self.tick_ms:                  # сильно отстали — догонять не будем
            self.dropped += int(self.acc // self.tick_ms)
            self.acc %= self.tick_ms
        return n

    @property
    def alpha(self) -> float:
        """Доля пути до следующего тика — для интерполяции на клиенте."""
        return self.acc / self.tick_ms
