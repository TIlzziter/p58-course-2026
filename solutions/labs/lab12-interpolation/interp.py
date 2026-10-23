"""Задачи 1–3. Интерполяция и буфер снимков."""
import bisect
import math


def clamp(x: float, lo: float, hi: float) -> float:
    return lo if x < lo else hi if x > hi else x


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def lerp_point(p, q, t: float) -> tuple[float, float]:
    return lerp(p[0], q[0], t), lerp(p[1], q[1], t)


def ease_out_quad(t: float) -> float:
    t = clamp(t, 0.0, 1.0)
    return 1 - (1 - t) ** 2


class SnapshotBuffer:
    """Снимки состояния сервера по времени. Хранит не больше size последних."""

    def __init__(self, size: int = 32):
        self.size = size
        self.times: list[float] = []
        self.states: list[dict] = []

    def add(self, t: float, state: dict) -> bool:
        """Опоздавший снимок старше самого старого или с уже известным временем — игнорируем (False)."""
        i = bisect.bisect_left(self.times, t)
        if i < len(self.times) and self.times[i] == t:
            return False
        if len(self.times) >= self.size and i == 0:
            return False
        self.times.insert(i, t)
        self.states.insert(i, state)
        if len(self.times) > self.size:
            del self.times[0], self.states[0]
        return True

    def sample(self, t: float):
        """(раньше, позже, alpha) для момента t. До первого — (s0, s0, 0), после последнего — (sN, sN, 1). Пусто → None."""
        if not self.times:
            return None
        if t <= self.times[0]:
            return self.states[0], self.states[0], 0.0
        if t >= self.times[-1]:
            return self.states[-1], self.states[-1], 1.0
        i = bisect.bisect_right(self.times, t)
        t0, t1 = self.times[i - 1], self.times[i]
        return self.states[i - 1], self.states[i], (t - t0) / (t1 - t0)


def blend(prev: dict, nxt: dict, alpha: float, teleport: float = 2.0) -> dict:
    """Позиции сущностей id → (x, y) между двумя снимками.

    Есть в обоих — lerp; прыжок дальше teleport клеток — без lerp: prev до alpha < 0.5, потом next.
    Только в next — появляется сразу в своей точке. Только в prev — исчезает (не рисуем).
    """
    out = {}
    for eid, q in nxt.items():
        if eid not in prev:
            out[eid] = (float(q[0]), float(q[1]))
            continue
        p = prev[eid]
        if math.dist(p, q) > teleport:
            src = p if alpha < 0.5 else q
            out[eid] = (float(src[0]), float(src[1]))
        else:
            out[eid] = lerp_point(p, q, alpha)
    return out
