"""Контест 5 · E4 (босс): поэтапное обновление копий сервиса."""


def rolling_plan(n: int, max_unavailable: int, max_surge: int, start: tuple[int, int] | None = None):
    """а) Состояния (старых, новых) после каждого шага, пока все n копий не станут новыми.

    Шаг: сначала запускаем новые, сколько позволяет surge (всего копий ≤ n + max_surge, новых ≤ n),
    затем гасим старые, пока работающих не меньше n − max_unavailable.
    """
    if max_unavailable < 0 or max_surge < 0 or (max_unavailable == 0 and max_surge == 0):
        raise ValueError("так обновить нельзя")
    old, new = start if start is not None else (n, 0)
    plan = []
    while old > 0 or new < n:
        new += max(0, min(n - new, n + max_surge - old - new))
        old -= max(0, min(old, old + new - (n - max_unavailable)))
        if plan and plan[-1] == (old, new):
            raise ValueError("нет прогресса")
        plan.append((old, new))
    return plan


def ready_ticks(checks: list[list[bool]], need: int) -> list[int | None]:
    """б) Для каждой новой копии — номер проверки (с нуля), после которой у неё need успешных подряд; иначе None."""
    out = []
    for seq in checks:
        streak, at = 0, None
        for i, ok in enumerate(seq):
            streak = streak + 1 if ok else 0
            if streak >= need:
                at = i
                break
        out.append(at)
    return out


def rollback_plan(n: int, max_unavailable: int, max_surge: int, state: tuple[int, int]):
    """в) Откат из состояния (старых, новых): те же правила, но «новыми» становятся старые. Состояния
    — снова в виде (старых, новых)."""
    old, new = state
    return [(o, nw) for nw, o in rolling_plan(n, max_unavailable, max_surge, start=(new, old))]
