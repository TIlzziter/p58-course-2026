"""Задачи 1–5, 7*. Аналитика игровых событий на pandas."""
import math
from datetime import timedelta

import pandas as pd

KNOWN = {"session_start", "match_start", "match_end"}


def load_events(path) -> pd.DataFrame:
    """Задача 1. Прочитать CSV событий.

    * ts — время в UTC (`pd.to_datetime(..., utc=True)`), user_id — int;
    * строки-дубликаты целиком убрать (клиент повторяет отправку при плохой сети);
    * события не из KNOWN выбросить;
    * отсортировать по ts (при равенстве — исходный порядок), индекс 0..n-1.
    """
    df = pd.read_csv(path)
    df["ts"] = pd.to_datetime(df["ts"], utc=True)
    df["user_id"] = df["user_id"].astype(int)
    df = df.drop_duplicates()
    df = df[df["event"].isin(KNOWN)]
    return df.sort_values("ts", kind="stable").reset_index(drop=True)


def dau(df: pd.DataFrame) -> pd.Series:
    """Задача 2. Уникальные игроки по дням (UTC). Индекс — даты (`datetime.date`) подряд от первой до последней,
    дни без игроков — 0. Имя серии — "dau"."""
    if df.empty:
        return pd.Series(dtype=int, name="dau")
    day = df["ts"].dt.date
    counts = df.groupby(day)["user_id"].nunique()
    full = [counts.index.min() + timedelta(days=i) for i in range((counts.index.max() - counts.index.min()).days + 1)]
    return counts.reindex(full, fill_value=0).astype(int).rename("dau")


def match_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Задача 3. По событиям match_end: для каждого дня — matches (число), median_s и p90_s (длительность,
    квантиль 0.9 с линейной интерполяцией, как по умолчанию в pandas), округлить до 1 знака.
    Индекс — дата, только дни с матчами."""
    m = df[df["event"] == "match_end"]
    g = m.groupby(m["ts"].dt.date)["duration_s"]
    out = pd.DataFrame({"matches": g.size(), "median_s": g.median(), "p90_s": g.quantile(0.9)})
    out.index.name = "day"
    return out.round({"median_s": 1, "p90_s": 1})


def retention(df: pd.DataFrame, days=(1, 7)) -> pd.DataFrame:
    """Задача 4. Когорты по дню первого события игрока. Для каждой когорты: size — сколько игроков, и для каждого
    N из days колонка dN — доля игроков когорты, у которых есть событие ровно в день cohort + N (округлить до 3).
    Когорта, для которой день cohort + N ещё не наступил (позже последнего дня в данных), — NaN, а не 0."""
    day = df["ts"].dt.date
    first = day.groupby(df["user_id"]).min().rename("cohort")
    active = set(zip(df["user_id"], day, strict=True))
    last_day = day.max()
    rows = {}
    for cohort, users in first.groupby(first).groups.items():
        row = {"size": len(users)}
        for n in days:
            target = cohort + timedelta(days=n)
            if target > last_day:
                row[f"d{n}"] = float("nan")
            else:
                row[f"d{n}"] = round(sum((u, target) in active for u in users) / len(users), 3)
        rows[cohort] = row
    out = pd.DataFrame.from_dict(rows, orient="index").sort_index()
    out.index.name = "cohort"
    out["size"] = out["size"].astype(int)
    return out


def balance(df: pd.DataFrame) -> dict:
    """Задача 5. Преимущество первого хода. У каждого матча (match_id) два события match_end — по игроку,
    side = "first"/"second", result = "win"/"loss"/"draw". Считаем по стороне first (одна строка на матч).

    Ответ: games, first_wins, second_wins, draws, first_win_rate = first_wins / (first_wins + second_wins)
    (решённые партии, округлить до 3; нет решённых — None) и p_value — двусторонний точный биномиальный тест
    «шанс 50/50» по решённым партиям, как в лабе 16 (округлить до 4)."""
    m = df[(df["event"] == "match_end") & (df["side"] == "first")].drop_duplicates("match_id")
    fw = int((m["result"] == "win").sum())
    sw = int((m["result"] == "loss").sum())
    dr = int((m["result"] == "draw").sum())
    n, k = fw + sw, min(fw, sw)
    p = 1.0 if n == 0 else min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)
    return {"games": len(m), "first_wins": fw, "second_wins": sw, "draws": dr,
            "first_win_rate": round(fw / n, 3) if n else None, "p_value": round(p, 4)}


def funnel(df: pd.DataFrame, steps: list[str]) -> list[int]:
    """Задача 7*. Упорядоченная воронка: сколько игроков сделали steps[0]; из них — steps[1] не раньше первого
    steps[0]; … — каждый шаг не раньше момента, когда игрок прошёл предыдущий (берём самое раннее подходящее
    событие). Ответ — список чисел той же длины, что steps."""
    counts = [0] * len(steps)
    for _, g in df.sort_values("ts", kind="stable").groupby("user_id"):
        t = None
        for i, step in enumerate(steps):
            ev = g[(g["event"] == step) & ((g["ts"] >= t) if t is not None else True)]
            if ev.empty:
                break
            t = ev["ts"].iloc[0]
            counts[i] += 1
    return counts
