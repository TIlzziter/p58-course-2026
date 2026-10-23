"""Задача 7*. Адаптивная задержка буфера по джиттеру."""


def percentile(values: list[float], q: float) -> float:
    """Ближайший ранг: элемент с индексом ceil(q·n) − 1 в отсортированном списке. Пусто → ValueError."""
    raise NotImplementedError


def render_delay(arrivals: list[float], tick_ms: float, q: float = 0.95, min_delay: float | None = None) -> int:
    """Задержка отрисовки, мс: tick + q-перцентиль |интервал − tick|, округлить вверх.
    Меньше двух прибытий → 2·tick. Не меньше min_delay (по умолчанию tick)."""
    raise NotImplementedError
