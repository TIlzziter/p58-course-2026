"""Рейтинг Эло (задача 2)."""
K = 32


def expected(ra: int, rb: int) -> float:
    """Ожидаемый счёт игрока A против B: от 0 до 1."""
    return 1 / (1 + 10 ** ((ra - rb) / 400))      # BUG? проверьте на 1200 против 1000


def update(ra: int, rb: int, score_a: float, k: int = K) -> tuple[int, int]:
    """Новые рейтинги после партии. score_a: 1 — победа A, 0.5 — ничья, 0 — поражение."""
    # TODO: проверка score_a; целые рейтинги; сумма рейтингов не должна меняться
    new_a = ra + k * (score_a - expected(ra, rb))
    new_b = rb + k * ((1 - score_a) - expected(rb, ra))
    return new_a, new_b
