"""Задача 2. RPO и RTO: сколько данных потеряем и как долго будем восстанавливаться."""
from datetime import datetime, timedelta


def data_loss(backups: list[datetime], incident: datetime) -> timedelta | None:
    """Сколько данных потеряем: от последнего бэкапа не позже incident до incident. Нет такого — None."""
    before = [b for b in backups if b <= incident]
    return incident - max(before) if before else None


def worst_rpo(backups: list[datetime]) -> timedelta:
    """Худший случай при таком расписании — наибольший промежуток между соседними бэкапами.
    Меньше двух бэкапов — ValueError."""
    if len(backups) < 2:
        raise ValueError("нужно хотя бы два бэкапа")
    s = sorted(backups)
    return max(b - a for a, b in zip(s, s[1:]))


def rto_estimate(size_mb: float, restore_mb_s: float, steps_s: list[float]) -> float:
    """Оценка времени восстановления, секунды: size_mb / restore_mb_s + сумма ручных шагов. 1 знак."""
    if restore_mb_s <= 0:
        raise ValueError("скорость должна быть > 0")
    return round(size_mb / restore_mb_s + sum(steps_s), 1)


def meets_targets(backups: list[datetime], rpo: timedelta, rto_s: float, size_mb: float,
                  restore_mb_s: float, steps_s: list[float]) -> dict:
    """Проверка целей: {"rpo_ok", "rto_ok", "worst_rpo_min" (минуты, 1 знак), "rto_s"}."""
    w = worst_rpo(backups)
    r = rto_estimate(size_mb, restore_mb_s, steps_s)
    return {"rpo_ok": w <= rpo, "rto_ok": r <= rto_s, "worst_rpo_min": round(w.total_seconds() / 60, 1), "rto_s": r}
