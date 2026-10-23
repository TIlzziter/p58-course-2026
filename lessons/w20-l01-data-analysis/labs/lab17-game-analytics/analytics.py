"""Задачи 1–5, 7*. Аналитика игровых событий на pandas."""
import math  # noqa: F401
from datetime import timedelta  # noqa: F401

import pandas as pd

KNOWN = {"session_start", "match_start", "match_end"}


def load_events(path) -> pd.DataFrame:
    """Задача 1. Прочитать CSV событий.

    * ts — время в UTC (`pd.to_datetime(..., utc=True)`), user_id — int;
    * строки-дубликаты целиком убрать (клиент повторяет отправку при плохой сети);
    * события не из KNOWN выбросить;
    * отсортировать по ts (при равенстве — исходный порядок), индекс 0..n-1.
    """
    # TODO: UTC, дубликаты, неизвестные события, сортировка и индекс
    df = pd.read_csv(path)
    df["ts"] = pd.to_datetime(df["ts"])
    return df


def dau(df: pd.DataFrame) -> pd.Series:
    """Задача 2. Уникальные игроки по дням (UTC). Индекс — даты (`datetime.date`) подряд от первой до последней,
    дни без игроков — 0. Имя серии — "dau"."""
    if df.empty:
        return pd.Series(dtype=int, name="dau")
    # TODO: уникальные игроки, а не события; дни без игроков — 0 (timedelta уже импортирован)
    return df.groupby(df["ts"].dt.date)["user_id"].count().rename("dau")


def match_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Задача 3. По событиям match_end: для каждого дня — matches (число), median_s и p90_s (длительность,
    квантиль 0.9 с линейной интерполяцией, как по умолчанию в pandas), округлить до 1 знака.
    Индекс — дата, только дни с матчами."""
    m = df[df["event"] == "match_end"]
    g = m.groupby(m["ts"].dt.date)["duration_s"]
    out = pd.DataFrame({"matches": g.size(), "median_s": g.median(), "p90_s": g.max()})  # TODO: квантиль 0.9
    out.index.name = "day"
    return out.round({"median_s": 1, "p90_s": 1})


def retention(df: pd.DataFrame, days=(1, 7)) -> pd.DataFrame:
    """Задача 4. Когорты по дню первого события игрока. Для каждой когорты: size — сколько игроков, и для каждого
    N из days колонка dN — доля игроков когорты, у которых есть событие ровно в день cohort + N (округлить до 3).
    Когорта, для которой день cohort + N ещё не наступил (позже последнего дня в данных), — NaN, а не 0."""
    raise NotImplementedError  # TODO


def balance(df: pd.DataFrame) -> dict:
    """Задача 5. Преимущество первого хода. У каждого матча (match_id) два события match_end — по игроку,
    side = "first"/"second", result = "win"/"loss"/"draw". Считаем по стороне first (одна строка на матч).

    Ответ: games, first_wins, second_wins, draws, first_win_rate = first_wins / (first_wins + second_wins)
    (решённые партии, округлить до 3; нет решённых — None) и p_value — двусторонний точный биномиальный тест
    «шанс 50/50» по решённым партиям, как в лабе 16 (округлить до 4)."""
    # TODO: одна строка на матч — по стороне first; p_value по точному тесту
    m = df[df["event"] == "match_end"]
    fw = int((m["result"] == "win").sum())
    sw = int((m["result"] == "loss").sum())
    dr = int((m["result"] == "draw").sum())
    n = fw + sw
    p = 1.0
    return {"games": len(m), "first_wins": fw, "second_wins": sw, "draws": dr,
            "first_win_rate": round(fw / n, 3), "p_value": round(p, 4)}


def funnel(df: pd.DataFrame, steps: list[str]) -> list[int]:
    """Задача 7*. Упорядоченная воронка: сколько игроков сделали steps[0]; из них — steps[1] не раньше первого
    steps[0]; … — каждый шаг не раньше момента, когда игрок прошёл предыдущий (берём самое раннее подходящее
    событие). Ответ — список чисел той же длины, что steps."""
    raise NotImplementedError  # TODO
