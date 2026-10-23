"""Контест 12 · E4 босс: автомасштабирование реплик."""
import math


def desired(current: int, util: float, target: float, lo: int = 1, hi: int = 10, tolerance: float = 0.1) -> int:
    """а) Формула HPA: ratio = util / target; |ratio − 1| ≤ tolerance — оставить current; иначе
    ceil(current · ratio) (с поправкой 1e-9 на ошибки float). Ограничить [lo, hi]."""
    ratio = util / target
    if abs(ratio - 1) <= tolerance:
        n = current
    else:
        n = math.ceil(current * ratio - 1e-9)
    return max(lo, min(hi, n))


def stabilize(recs: list[int], window: int) -> list[int]:
    """б) Стабилизация: в момент i реплик = max(recs[i − window + 1 .. i]) — вверх сразу, вниз только
    когда все рекомендации окна ниже."""
    return [max(recs[max(0, i - window + 1): i + 1]) for i in range(len(recs))]


def simulate(load: list[float], capacity: float, target: float = 0.6, start: int = 1, window: int = 3,
             lo: int = 1, hi: int = 10) -> dict:
    """в) Поминутно: обслужено min(load, replicas · capacity), потеряно — остальное. util = load / (replicas ·
    capacity) (может быть > 1). Рекомендация desired(replicas, util, target, lo, hi), реплики на следующую
    минуту — stabilize по последним window рекомендациям. Ответ: {"replicas": [на каждой минуте],
    "dropped": всего потеряно, "peak": max реплик}."""
    replicas, recs, hist, dropped = start, [], [], 0.0
    for x in load:
        hist.append(replicas)
        cap = replicas * capacity
        dropped += max(0.0, x - cap)
        recs.append(desired(replicas, x / cap, target, lo, hi))
        replicas = max(recs[-window:])
    return {"replicas": hist, "dropped": round(dropped, 1), "peak": max(hist)}
