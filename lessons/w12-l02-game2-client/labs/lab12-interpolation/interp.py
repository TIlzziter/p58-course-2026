"""Задачи 1–3. Интерполяция и буфер снимков."""


def clamp(x: float, lo: float, hi: float) -> float:
    return lo if x < lo else hi if x > hi else x


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def lerp_point(p, q, t: float) -> tuple[float, float]:
    raise NotImplementedError


def ease_out_quad(t: float) -> float:
    """Быстрый старт, плавная остановка: 1 − (1 − t)². t вне [0, 1] прижимаем к краю."""
    return 1 - (1 - t) ** 2


class SnapshotBuffer:
    """Снимки состояния сервера по времени. Хранит не больше size последних."""

    def __init__(self, size: int = 32):
        self.size = size
        self.times: list[float] = []
        self.states: list[dict] = []

    def add(self, t: float, state: dict) -> bool:
        """Вставить по порядку времени. Повтор времени или снимок старше самого старого в полном буфере → False."""
        self.times.append(t)
        self.states.append(state)
        return True

    def sample(self, t: float):
        """(раньше, позже, alpha) для момента t. До первого — (s0, s0, 0), после последнего — (sN, sN, 1). Пусто → None."""
        prev, nxt = self.states[-2], self.states[-1]
        t0, t1 = self.times[-2], self.times[-1]
        return prev, nxt, (t - t0) / (t1 - t0)


def blend(prev: dict, nxt: dict, alpha: float, teleport: float = 2.0) -> dict:
    """Позиции сущностей id → (x, y) между двумя снимками.

    Есть в обоих — lerp; прыжок дальше teleport клеток — без lerp: prev до alpha < 0.5, потом next.
    Только в next — появляется сразу в своей точке. Только в prev — исчезает (не рисуем).
    """
    return {eid: lerp_point(prev[eid], q, alpha) for eid, q in nxt.items()}
