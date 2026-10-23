"""Задачи 5–6. Предсказание на клиенте, сверка с сервером, экстраполяция."""
from interp import clamp

MOVES = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}


def apply(pos: tuple[int, int], cmd: str, width: int, height: int) -> tuple[int, int]:
    dx, dy = MOVES[cmd]
    return int(clamp(pos[0] + dx, 0, width - 1)), int(clamp(pos[1] + dy, 0, height - 1))


class Predictor:
    """Игрок двигается сразу, не дожидаясь сервера. Сервер присылает (позиция, последний обработанный seq)."""

    def __init__(self, pos, width: int, height: int):
        self.pos = tuple(pos)
        self.width, self.height = width, height
        self.seq = 0
        self.pending: list[tuple[int, str]] = []
        self.corrections = 0

    def local(self, cmd: str) -> int:
        self.seq += 1
        self.pending.append((self.seq, cmd))
        self.pos = apply(self.pos, cmd, self.width, self.height)
        return self.seq

    def server(self, pos, last_seq: int) -> None:
        self.pending = [(s, c) for s, c in self.pending if s > last_seq]
        predicted = self.pos
        p = tuple(pos)
        for _, c in self.pending:
            p = apply(p, c, self.width, self.height)
        if p != predicted:
            self.corrections += 1
        self.pos = p


def extrapolate(p, v, dt_ms: float, max_ms: float):
    """Позиция через dt_ms по скорости v (клеток в секунду), но не дальше max_ms вперёд. dt < 0 → p."""
    dt = clamp(dt_ms, 0, max_ms) / 1000
    return p[0] + v[0] * dt, p[1] + v[1] * dt
