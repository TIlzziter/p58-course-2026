"""Задача 7*. Учения: бэкап → авария → восстановление → проверка, с замером времени."""
import sqlite3
import time  # noqa: F401
from datetime import datetime
from pathlib import Path

from backup import make_backup, restore  # noqa: F401
from demo import table_counts  # noqa: F401


def disaster(db_path: str | Path, kind: str) -> None:
    """Авария: "drop" — удалить таблицу matches; "delete" — удалить файл базы; "corrupt" — затереть
    первые 100 байт нулями. Другое — ValueError."""
    p = Path(db_path)
    if kind == "drop":
        con = sqlite3.connect(p)
        con.execute("DROP TABLE matches")
        con.commit()
        con.close()
    elif kind == "delete":
        p.unlink()
    elif kind == "corrupt":
        with open(p, "r+b") as f:
            f.write(b"\0" * 100)
    else:
        raise ValueError(kind)


def drill(db_path: str | Path, backup_dir: str | Path, now: datetime, kind: str = "drop") -> dict:
    """Учения: запомнить строки → make_backup → disaster(kind) → restore в db_path → сравнить строки.
    Ответ: {"ok": строки совпали, "rows": число строк по таблицам после восстановления,
    "backup": имя файла, "restore_s": секунды на restore (perf_counter, ≥ 0)}."""
    raise NotImplementedError("TODO")
