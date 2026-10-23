import pytest
from indexes import QUERIES, add_indexes, make_db, plan, uses_full_scan

PARAMS = {"history": (42,), "room_top": ("chess",), "recent": ("2027-04-25",)}


@pytest.fixture
def conn():
    return make_db(5000)


def test_without_indexes_everything_scans(conn):
    for name, sql in QUERIES.items():
        assert uses_full_scan(conn, sql, PARAMS[name]), name


def test_with_indexes_no_scans(conn):
    created = add_indexes(conn)
    assert 1 <= len(created) <= 3
    names = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type = 'index'")}
    assert set(created) <= names
    for name, sql in QUERIES.items():
        assert not uses_full_scan(conn, sql, PARAMS[name]), (name, plan(conn, sql, PARAMS[name]))


def test_history_no_sort(conn):
    add_indexes(conn)
    p = plan(conn, QUERIES["history"], PARAMS["history"])
    assert "TEMP B-TREE FOR ORDER BY" not in p


def test_results_unchanged():
    a, b = make_db(3000), make_db(3000)
    add_indexes(b)
    for name, sql in QUERIES.items():
        assert sorted(a.execute(sql, PARAMS[name]).fetchall()) == sorted(b.execute(sql, PARAMS[name]).fetchall())
