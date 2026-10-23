"""Задача 1. Ротация бэкапов «дед — отец — сын» (GFS)."""
from datetime import datetime, timedelta


def _newest_by(backups, key, periods):
    best = {}
    for b in backups:
        k = key(b)
        if k in periods and (k not in best or b > best[k]):
            best[k] = b
    return set(best.values())


def keep(backups: list[datetime], now: datetime, daily: int = 7, weekly: int = 4, monthly: int = 6) -> set[datetime]:
    """Какие бэкапы оставить. Бэкапы позже now не учитываем вовсе (и не удаляем).
    * daily: в каждом из последних daily календарных дней (сегодня, вчера, …) — самый свежий бэкап дня;
    * weekly: в каждой из последних weekly недель ISO (текущая, прошлая, …) — самый свежий бэкап недели;
    * monthly: в каждом из последних monthly календарных месяцев (текущий, прошлый, …) — самый свежий;
    * самый свежий бэкап вообще — всегда.
    """
    past = [b for b in backups if b <= now]
    if not past:
        return set()
    days = {(now - timedelta(days=i)).date() for i in range(daily)}
    weeks = {(now - timedelta(weeks=i)).isocalendar()[:2] for i in range(weekly)}
    months = set()
    y, m = now.year, now.month
    for _ in range(monthly):
        months.add((y, m))
        y, m = (y, m - 1) if m > 1 else (y - 1, 12)
    result = {max(past)}
    result |= _newest_by(past, lambda b: b.date(), days)
    result |= _newest_by(past, lambda b: tuple(b.isocalendar()[:2]), weeks)
    result |= _newest_by(past, lambda b: (b.year, b.month), months)
    return result


def to_delete(backups: list[datetime], now: datetime, **limits) -> list[datetime]:
    """Что удалить: прошлые бэкапы не из keep(...), по возрастанию."""
    k = keep(backups, now, **limits)
    return sorted(b for b in backups if b <= now and b not in k)
