"""Задача 1. Ротация бэкапов «дед — отец — сын» (GFS)."""
from datetime import datetime, timedelta  # noqa: F401


def keep(backups: list[datetime], now: datetime, daily: int = 7, weekly: int = 4, monthly: int = 6) -> set[datetime]:
    """Какие бэкапы оставить. Бэкапы позже now не учитываем вовсе (и не удаляем).
    * daily: в каждом из последних daily календарных дней (сегодня, вчера, …) — самый свежий бэкап дня;
    * weekly: в каждой из последних weekly недель ISO (текущая, прошлая, …) — самый свежий бэкап недели;
    * monthly: в каждом из последних monthly календарных месяцев (текущий, прошлый, …) — самый свежий;
    * самый свежий бэкап вообще — всегда.
    """
    raise NotImplementedError("TODO")


def to_delete(backups: list[datetime], now: datetime, **limits) -> list[datetime]:
    """Что удалить: прошлые бэкапы не из keep(...), по возрастанию."""
    raise NotImplementedError("TODO")
