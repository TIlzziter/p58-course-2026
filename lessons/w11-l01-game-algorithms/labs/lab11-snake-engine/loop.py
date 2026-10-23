"""Задача 6. Игровой цикл с фиксированным шагом и буфером ввода."""
from collections.abc import Callable


class GameLoop:
    def __init__(self, tick_ms: int, max_catchup: int = 5, buffer: int = 2):
        self.tick_ms, self.max_catchup, self.buffer = tick_ms, max_catchup, buffer
        self.acc = 0.0
        self.pending: dict[str, str] = {}
        self.dropped = 0

    def push_input(self, name: str, direction: str) -> None:
        self.pending[name] = direction

    def take_inputs(self) -> dict[str, str]:
        out, self.pending = self.pending, {}
        return out

    def advance(self, elapsed_ms: float, on_tick: Callable[[dict[str, str]], None]) -> int:
        self.acc += elapsed_ms
        if self.acc >= self.tick_ms:
            on_tick(self.take_inputs())
            self.acc = 0
            return 1
        return 0

    @property
    def alpha(self) -> float:
        """Доля пути до следующего тика — для интерполяции на клиенте."""
        return self.acc / self.tick_ms
