import gzip
import hashlib
import json
import sqlite3
from datetime import datetime

import pytest
from backup import backup_name, make_backup, read_manifest

NOW = datetime(2027, 4, 26, 3, 0)


def test_name():
    assert backup_name(NOW) == "game-20270426-0300.db.gz"
    assert backup_name(datetime(2027, 1, 2, 23, 5)) == "game-20270102-2305.db.gz"


def test_backup_file_and_manifest(db, tmp_path):
    out = tmp_path / "backups"
    p = make_backup(db, out, NOW)
    assert p == out / "game-20270426-0300.db.gz" and p.exists()
    raw = gzip.decompress(p.read_bytes())
    assert raw.startswith(b"SQLite format 3\0")
    m = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    assert m == read_manifest(out) and len(m) == 1
    e = m[0]
    assert e["file"] == p.name and e["size"] == p.stat().st_size and e["created"] == "2027-04-26T03:00:00"
    assert e["sha256"] == hashlib.sha256(p.read_bytes()).hexdigest()
    assert e["tables"] == {"matches": 500, "players": 50}


def test_manifest_appends_and_no_overwrite(db, tmp_path):
    out = tmp_path / "b"
    make_backup(db, out, NOW)
    make_backup(db, out, datetime(2027, 4, 27, 3, 0))
    assert [e["file"] for e in read_manifest(out)] == ["game-20270426-0300.db.gz", "game-20270427-0300.db.gz"]
    with pytest.raises(FileExistsError):
        make_backup(db, out, NOW)
    assert len(read_manifest(out)) == 2


def test_consistent_copy_with_open_transaction(db, tmp_path):
    con = sqlite3.connect(db)
    con.execute("INSERT INTO players VALUES (999, 'ghost', 1000)")  # не закоммичено
    try:
        e = None
        p = make_backup(db, tmp_path / "b", NOW)
        e = read_manifest(p.parent)[0]
    finally:
        con.rollback()
        con.close()
    assert e["tables"]["players"] == 50
