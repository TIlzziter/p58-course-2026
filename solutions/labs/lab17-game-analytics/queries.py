"""Задача 6. SQL-аналитика: та же таблица events в SQLite (в проекте — PostgreSQL, синтаксис тот же)."""

TOP_PLAYERS = """
WITH per_user AS (
    SELECT user_id,
           COUNT(*) AS matches,
           SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) AS wins
    FROM events
    WHERE event = 'match_end'
    GROUP BY user_id
)
SELECT user_id, matches, wins,
       ROUND(1.0 * wins / matches, 3) AS win_rate,
       DENSE_RANK() OVER (ORDER BY wins DESC) AS place
FROM per_user
ORDER BY place, user_id
LIMIT :n
"""

DAILY_RUNNING = """
WITH daily AS (
    SELECT DATE(ts) AS day, COUNT(*) AS matches
    FROM events
    WHERE event = 'match_end' AND side = 'first'
    GROUP BY DATE(ts)
)
SELECT day, matches,
       SUM(matches) OVER (ORDER BY day) AS total,
       matches - LAG(matches, 1, 0) OVER (ORDER BY day) AS delta
FROM daily
ORDER BY day
"""


def top_players(conn, n: int) -> list[tuple]:
    """(user_id, matches, wins, win_rate, place): по событиям match_end; place — DENSE_RANK по wins (больше — выше);
    порядок — place, затем user_id; не больше n строк."""
    return conn.execute(TOP_PLAYERS, {"n": n}).fetchall()


def daily_running(conn) -> list[tuple]:
    """(day, matches, total, delta): матчей за день (одна строка match_end с side='first' на матч), нарастающий
    итог и изменение к предыдущему дню с матчами (для первого — само число)."""
    return conn.execute(DAILY_RUNNING).fetchall()
