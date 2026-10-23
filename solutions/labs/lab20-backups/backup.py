"""Задачи 3–4. Бэкап с манифестом, проверка и восстановление."""
import gzip
import hashlib
import json
import os
import shutil
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path

from demo import table_counts

MANIFEST = "manifest.json"


def backup_name(now: datetime) -> str:
    """Имя файла бэкапа: game-ГГГГММДД-ЧЧММ.db.gz."""
    return f"game-{now:%Y%m%d-%H%M}.db.gz"


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
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / backup_name(now)
    if target.exists():
        raise FileExistsError(target)
    with tempfile.TemporaryDirectory() as tmp:
        raw = Path(tmp) / "copy.db"
        src, dst = sqlite3.connect(db_path), sqlite3.connect(raw)
        try:
            src.backup(dst)
        finally:
            dst.close()
            src.close()
        counts = table_counts(raw)
        with open(raw, "rb") as fi, gzip.open(target, "wb") as fo:
            shutil.copyfileobj(fi, fo)
    entries = read_manifest(out_dir)
    entries.append({"file": target.name, "sha256": sha256_file(target), "size": target.stat().st_size,
                    "created": now.isoformat(), "tables": counts})
    (out_dir / MANIFEST).write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    return target


def verify(backup_path: str | Path) -> bool:
    """Задача 4. Файл есть в манифесте своей папки и его sha256 совпадает. Нет записи — False."""
    p = Path(backup_path)
    if not p.exists():
        return False
    for e in read_manifest(p.parent):
        if e["file"] == p.name:
            return e["sha256"] == sha256_file(p)
    return False


def restore(backup_path: str | Path, target_db: str | Path) -> dict[str, int]:
    """Задача 4. Восстановить: verify (иначе ValueError) → распаковать во временный файл рядом с target_db →
    PRAGMA integrity_check == "ok" и число строк как в манифесте (иначе ValueError, target_db не тронут) →
    атомарно заменить target_db (os.replace). Возвращает число строк по таблицам."""
    p, target = Path(backup_path), Path(target_db)
    if not verify(p):
        raise ValueError("бэкап не прошёл проверку sha256")
    entry = next(e for e in read_manifest(p.parent) if e["file"] == p.name)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=target.parent, suffix=".restore")
    os.close(fd)
    tmp = Path(tmp_name)
    try:
        with gzip.open(p, "rb") as fi, open(tmp, "wb") as fo:
            shutil.copyfileobj(fi, fo)
        con = sqlite3.connect(tmp)
        try:
            ok = con.execute("PRAGMA integrity_check").fetchone()[0]
        finally:
            con.close()
        if ok != "ok":
            raise ValueError(f"integrity_check: {ok}")
        counts = table_counts(tmp)
        if counts != entry["tables"]:
            raise ValueError(f"строки не совпали: {counts} != {entry['tables']}")
        os.replace(tmp, target)
        return counts
    finally:
        tmp.unlink(missing_ok=True)
