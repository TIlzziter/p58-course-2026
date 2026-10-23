"""Рейтинг Эло."""
K = 32


def expected(ra: int, rb: int) -> float:
    """Ожидаемый счёт игрока A против B: от 0 до 1."""
    return 1 / (1 + 10 ** ((rb - ra) / 400))


def update(ra: int, rb: int, score_a: float, k: int = K) -> tuple[int, int]:
    """Новые рейтинги после партии. score_a: 1 — победа A, 0.5 — ничья, 0 — поражение.

    Изменение считаем один раз и округляем, а B получает ровно противоположное — сумма рейтингов сохраняется.
    """
    if score_a not in (0, 0.5, 1):
        raise ValueError("score_a должен быть 0, 0.5 или 1")
    delta = round(k * (score_a - expected(ra, rb)))
    return ra + delta, rb - delta
