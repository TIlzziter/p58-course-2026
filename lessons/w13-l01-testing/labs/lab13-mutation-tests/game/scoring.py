"""Очки и рейтинг после партии."""


def points(place: int, players: int) -> int:
    """Очки за место в партии на 2–4 игрока.

    Последнее место — 0, каждое место выше — на 1 больше, победитель получает ещё +2.
    Пример: 4 игрока → места 1, 2, 3, 4 дают 5, 2, 1, 0.
    Число игроков вне 2..4 или место вне 1..players — ValueError.
    """
    if not 2 <= players <= 4:
        raise ValueError("игроков должно быть от 2 до 4")
    if place < 1 or place > players:
        raise ValueError("нет такого места")
    base = players - place
    return base + 2 if place == 1 else base


def streak_bonus(results: list[bool]) -> int:
    """Бонус за серию побед в конце списка: от 3 побед подряд — 5 за каждую после второй, но не больше 25."""
    n = 0
    for won in reversed(results):
        if not won:
            break
        n += 1
    if n < 3:
        return 0
    return min((n - 2) * 5, 25)


def elo(ra: int, rb: int, score_a: float, k: int = 32) -> tuple[int, int]:
    """Новые рейтинги после партии A против B. score_a: 1 — победа A, 0.5 — ничья, 0 — поражение."""
    if score_a not in (0, 0.5, 1):
        raise ValueError("score_a: 0, 0.5 или 1")
    expected_a = 1 / (1 + 10 ** ((rb - ra) / 400))
    delta = k * (score_a - expected_a)
    return round(ra + delta), round(rb - delta)
