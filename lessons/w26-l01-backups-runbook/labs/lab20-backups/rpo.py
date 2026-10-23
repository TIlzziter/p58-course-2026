"""Задача 2. RPO и RTO: сколько данных потеряем и как долго будем восстанавливаться."""
from datetime import datetime, timedelta


def data_loss(backups: list[datetime], incident: datetime) -> timedelta | None:
    """Сколько данных потеряем: от последнего бэкапа не позже incident до incident. Нет такого — None."""
    raise NotImplementedError("TODO")


def worst_rpo(backups: list[datetime]) -> timedelta:
    """Худший случай при таком расписании — наибольший промежуток между соседними бэкапами.
    Меньше двух бэкапов — ValueError."""
    raise NotImplementedError("TODO")


def rto_estimate(size_mb: float, restore_mb_s: float, steps_s: list[float]) -> float:
    """Оценка времени восстановления, секунды: size_mb / restore_mb_s + сумма ручных шагов. 1 знак."""
    raise NotImplementedError("TODO")


def meets_targets(backups: list[datetime], rpo: timedelta, rto_s: float, size_mb: float,
                  restore_mb_s: float, steps_s: list[float]) -> dict:
    """Проверка целей: {"rpo_ok", "rto_ok", "worst_rpo_min" (минуты, 1 знак), "rto_s"}."""
    raise NotImplementedError("TODO")
