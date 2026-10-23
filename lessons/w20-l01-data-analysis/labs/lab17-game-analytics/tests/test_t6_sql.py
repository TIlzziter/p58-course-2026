from queries import daily_running, top_players


def test_top(small_db):
    assert top_players(small_db, 10) == [
        (1, 3, 2, 0.667, 1), (4, 1, 1, 1.0, 2), (2, 2, 0, 0.0, 3), (3, 2, 0, 0.0, 3)]
    assert top_players(small_db, 2) == [(1, 3, 2, 0.667, 1), (4, 1, 1, 1.0, 2)]


def test_running(small_db):
    assert daily_running(small_db) == [
        ("2027-03-01", 1, 1, 1), ("2027-03-02", 2, 3, 1), ("2027-03-04", 1, 4, -1)]


def test_sql_uses_window_functions():
    import queries
    assert "DENSE_RANK" in queries.TOP_PLAYERS.upper()
    assert "OVER" in queries.DAILY_RUNNING.upper() and "LAG" in queries.DAILY_RUNNING.upper()
