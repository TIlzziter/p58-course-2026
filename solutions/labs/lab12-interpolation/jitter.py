"""Задача 7*. Адаптивная задержка буфера по джиттеру."""
import math


def percentile(values: list[float], q: float) -> float:
    """Ближайший ранг: элемент с индексом ceil(q·n) − 1 в отсортированном списке."""
    if not values:
        raise ValueError("пусто")
    s = sorted(values)
    return s[max(0, math.ceil(q * len(s)) - 1)]


def render_delay(arrivals: list[float], tick_ms: float, q: float = 0.95, min_delay: float | None = None) -> int:
    """Задержка отрисовки, мс: tick + q-перцентиль |интервал − tick|, округлить вверх.
    Меньше двух прибытий → 2·tick. Не меньше min_delay (по умолчанию tick)."""
    if len(arrivals) < 2:
        return math.ceil(2 * tick_ms)
    gaps = [b - a for a, b in zip(arrivals, arrivals[1:])]
    jitter = percentile([abs(g - tick_ms) for g in gaps], q)
    return math.ceil(max(tick_ms + jitter, min_delay if min_delay is not None else tick_ms))
