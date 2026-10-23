import gzip
import sqlite3
from datetime import datetime

import pytest
from backup import make_backup, restore, verify
from demo import table_counts

NOW = datetime(2027, 4, 26, 3, 0)


def test_verify(db, tmp_path):
    p = make_backup(db, tmp_path / "b", NOW)
    assert verify(p)
    data = bytearray(p.read_bytes())
    data[-10] ^= 0xFF
    p.write_bytes(bytes(data))
    assert not verify(p)
    assert not verify(tmp_path / "b" / "nope.db.gz")


def test_verify_not_in_manifest(db, tmp_path):
    p = make_backup(db, tmp_path / "b", NOW)
    other = p.with_name("game-20990101-0000.db.gz")
    other.write_bytes(p.read_bytes())
    assert not verify(other)


def test_restore_roundtrip(db, tmp_path):
    p = make_backup(db, tmp_path / "b", NOW)
    con = sqlite3.connect(db)
    con.execute("DELETE FROM matches")
    con.commit()
    con.close()
    assert restore(p, db) == {"matches": 500, "players": 50}
    assert table_counts(db) == {"matches": 500, "players": 50}
    assert not list(db.parent.glob("*.restore"))


def test_restore_to_new_place(db, tmp_path):
    p = make_backup(db, tmp_path / "b", NOW)
    target = tmp_path / "new" / "game.db"
    restore(p, target)
    assert table_counts(target)["players"] == 50


def test_restore_bad_sha_keeps_target(db, tmp_path):
    p = make_backup(db, tmp_path / "b", NOW)
    p.write_bytes(gzip.compress(b"garbage"))
    before = db.read_bytes()
    with pytest.raises(ValueError):
        restore(p, db)
    assert db.read_bytes() == before


def test_restore_counts_mismatch(db, tmp_path):
    import json

    p = make_backup(db, tmp_path / "b", NOW)
    m = tmp_path / "b" / "manifest.json"
    data = json.loads(m.read_text(encoding="utf-8"))
    data[0]["tables"]["players"] = 51
    m.write_text(json.dumps(data), encoding="utf-8")
    before = db.read_bytes()
    with pytest.raises(ValueError):
        restore(p, db)
    assert db.read_bytes() == before and not list(db.parent.glob("*.restore"))
