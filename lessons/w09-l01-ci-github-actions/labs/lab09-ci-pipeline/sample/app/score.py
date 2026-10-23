"""Маленький модуль игры — чтобы конвейеру было что проверять."""


def combo_bonus(streak: int) -> int:
    """Бонус за серию попаданий: 0 до трёх подряд, дальше по 5 очков за каждое сверх двух."""
    if streak < 0:
        raise ValueError("серия не бывает отрицательной")
    return max(0, streak - 2) * 5


def total(hits: list[bool]) -> int:
    score, streak = 0, 0
    for hit in hits:
        streak = streak + 1 if hit else 0
        score += (10 + combo_bonus(streak)) if hit else 0
    return score
