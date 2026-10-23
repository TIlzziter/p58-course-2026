"""Задачи 3–4. Бэкап с манифестом, проверка и восстановление."""
import gzip  # noqa: F401
import hashlib
import json
import os  # noqa: F401
import shutil  # noqa: F401
import sqlite3  # noqa: F401
import tempfile  # noqa: F401
from datetime import datetime
from pathlib import Path

from demo import table_counts  # noqa: F401

MANIFEST = "manifest.json"


def backup_name(now: datetime) -> str:
    """Имя файла бэкапа: game-ГГГГММДД-ЧЧММ.db.gz."""
    raise NotImplementedError("TODO")


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def read_manifest(out_dir: str | Path) -> list[dict]:
    p = Path(out_dir) / MANIFEST
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []


def make_backup(db_path: str | Path, out_dir: str | Path, now: datetime) -> Path:
    """Задача 3. Согласованная копия через sqlite3 backup API (не копированием файла!), сжатие gzip,
    запись в манифест out_dir/manifest.json — список словарей
    {"file": имя, "sha256": от .gz, "size": байт .gz, "created": now.isoformat(), "tables": {таблица: строк}}.
    Бэкап с таким именем уже есть — FileExistsError. Возвращает путь к .gz."""
    raise NotImplementedError("TODO")


def verify(backup_path: str | Path) -> bool:
    """Задача 4. Файл есть в манифесте своей папки и его sha256 совпадает. Нет записи — False."""
    raise NotImplementedError("TODO")


def restore(backup_path: str | Path, target_db: str | Path) -> dict[str, int]:
    """Задача 4. Восстановить: verify (иначе ValueError) → распаковать во временный файл рядом с target_db →
    PRAGMA integrity_check == "ok" и число строк как в манифесте (иначе ValueError, target_db не тронут) →
    атомарно заменить target_db (os.replace). Возвращает число строк по таблицам."""
    raise NotImplementedError("TODO")
