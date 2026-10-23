from datetime import datetime

import pytest
from demo import table_counts
from drill import disaster, drill

NOW = datetime(2027, 4, 26, 3, 0)


@pytest.mark.parametrize("kind", ["drop", "delete", "corrupt"])
def test_drill(db, tmp_path, kind):
    r = drill(db, tmp_path / "b", NOW, kind)
    assert r["ok"] is True and r["rows"] == {"matches": 500, "players": 50}
    assert r["backup"] == "game-20270426-0300.db.gz" and r["restore_s"] >= 0
    assert table_counts(db) == r["rows"]


def test_disaster_really_breaks(db):
    disaster(db, "drop")
    assert "matches" not in table_counts(db)
    with pytest.raises(ValueError):
        disaster(db, "meteor")
