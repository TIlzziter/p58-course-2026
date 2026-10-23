"""Задача 7*. Учения: бэкап → авария → восстановление → проверка, с замером времени."""
import sqlite3
import time
from datetime import datetime
from pathlib import Path

from backup import make_backup, restore
from demo import table_counts


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
    before = table_counts(db_path)
    b = make_backup(db_path, backup_dir, now)
    disaster(db_path, kind)
    t0 = time.perf_counter()
    rows = restore(b, db_path)
    dt = time.perf_counter() - t0
    return {"ok": rows == before, "rows": rows, "backup": b.name, "restore_s": dt}
