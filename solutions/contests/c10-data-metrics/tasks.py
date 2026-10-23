"""Контест 10 · Данные и метрики — эталонные решения A1–D3."""
import math
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone

# ---------- A. Агрегаты ----------

def percentile(xs: list[float], p: float) -> float:
    """A1. Перцентиль с линейной интерполяцией: позиция (n−1)·p/100 в отсортированном списке; округлить до 2."""
    if not xs or not 0 <= p <= 100:
        raise ValueError("пустой список или p вне 0..100")
    s = sorted(xs)
    pos = (len(s) - 1) * p / 100
    lo = math.floor(pos)
    hi = min(lo + 1, len(s) - 1)
    return round(s[lo] + (s[hi] - s[lo]) * (pos - lo), 2)


def moving_average(xs: list[float], k: int) -> list[float | None]:
    """A2. Скользящее среднее по последним k значениям; первые k−1 — None; округлить до 2."""
    out, window = [], 0.0
    for i, x in enumerate(xs):
        window += x
        if i >= k:
            window -= xs[i - k]
        out.append(round(window / k, 2) if i >= k - 1 else None)
    return out


def histogram(xs: list[float], lo: float, hi: float, bins: int) -> list[int]:
    """A3. bins корзин равной ширины на [lo, hi]; корзина i — [lo+i·w, lo+(i+1)·w), последняя включает hi.
    Значения вне [lo, hi] не считаем."""
    w = (hi - lo) / bins
    counts = [0] * bins
    for x in xs:
        if lo <= x <= hi:
            counts[min(int((x - lo) / w), bins - 1)] += 1
    return counts


def welford(xs):
    """A4*. Один проход по потоку: (n, среднее, выборочное стандартное отклонение), округлить до 4.
    n < 2 — отклонение 0.0; пустой поток — (0, 0.0, 0.0)."""
    n, mean, m2 = 0, 0.0, 0.0
    for x in xs:
        n += 1
        d = x - mean
        mean += d / n
        m2 += d * (x - mean)
    std = math.sqrt(m2 / (n - 1)) if n > 1 else 0.0
    return n, round(mean, 4), round(std, 4)


# ---------- B. Время и когорты ----------

def to_local_day(ts: str, offset_hours: int) -> str:
    """B1. "2027-03-01T22:30:00Z" и сдвиг пояса в часах → локальная дата "YYYY-MM-DD"."""
    t = datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(timezone(timedelta(hours=offset_hours)))
    return t.date().isoformat()


def dau_series(events: list[tuple[int, str]], start: str, end: str) -> list[int]:
    """B2. События (user, "YYYY-MM-DD") → уникальных игроков в каждый день от start до end включительно."""
    by_day = defaultdict(set)
    for user, d in events:
        by_day[d].add(user)
    d0, d1 = date.fromisoformat(start), date.fromisoformat(end)
    return [len(by_day[(d0 + timedelta(days=i)).isoformat()]) for i in range((d1 - d0).days + 1)]


def retention_matrix(events: list[tuple[int, str]], max_day: int) -> dict[str, list[float | None]]:
    """B3. Когорта — день первого события игрока. Для N = 0..max_day — доля когорты с событием в день cohort+N
    (округлить до 2); день позже последнего дня в данных — None. Ключи по возрастанию."""
    active = {(u, date.fromisoformat(d)) for u, d in events}
    first: dict[int, date] = {}
    for u, d in active:
        if u not in first or d < first[u]:
            first[u] = d
    last = max(d for _, d in active)
    cohorts = defaultdict(list)
    for u, d in first.items():
        cohorts[d].append(u)
    out = {}
    for c in sorted(cohorts):
        users = cohorts[c]
        row = []
        for n in range(max_day + 1):
            t = c + timedelta(days=n)
            row.append(None if t > last else round(sum((u, t) in active for u in users) / len(users), 2))
        out[c.isoformat()] = row
    return out


# ---------- C. Как в SQL ----------

def ranks(scores: list[int]) -> tuple[list[int], list[int]]:
    """C1. Места по убыванию очков: (RANK, DENSE_RANK) для каждого элемента в исходном порядке."""
    s = sorted(scores, reverse=True)
    rank = {}
    for i, v in enumerate(s):
        rank.setdefault(v, i + 1)
    dense = {v: i + 1 for i, v in enumerate(sorted(set(scores), reverse=True))}
    return [rank[v] for v in scores], [dense[v] for v in scores]


def running_by_user(rows: list[tuple[str, str, int]]) -> list[int]:
    """C2. SUM(value) OVER (PARTITION BY user ORDER BY day): строки (user, day, value) с разными day у игрока,
    ответ — в исходном порядке строк."""
    order = sorted(range(len(rows)), key=lambda i: (rows[i][0], rows[i][1]))
    acc, out = defaultdict(int), [0] * len(rows)
    for i in order:
        u, _, v = rows[i]
        acc[u] += v
        out[i] = acc[u]
    return out


def pivot(rows: list[tuple[str, str, int]]) -> tuple[list[str], list[tuple[str, list[int]]]]:
    """C3. Сводная таблица: (строка, столбец, число) → сумма по клеткам; строки и столбцы по алфавиту, пусто — 0.
    Ответ — (столбцы, [(строка, [значения по столбцам])])."""
    cells = defaultdict(int)
    for r, c, v in rows:
        cells[r, c] += v
    cols = sorted({c for _, c, _ in rows})
    rs = sorted({r for r, _, _ in rows})
    return cols, [(r, [cells.get((r, c), 0) for c in cols]) for r in rs]


def sessionize(events: list[tuple[int, int]], gap: int) -> dict[int, list[tuple[int, int, int]]]:
    """C4*. События (user, ts в секундах) в любом порядке → сессии игрока: новая сессия, если пауза
    больше gap. Сессия — (начало, конец, число событий). Ключи по возрастанию user."""
    by_user = defaultdict(list)
    for u, t in events:
        by_user[u].append(t)
    out = {}
    for u in sorted(by_user):
        ts = sorted(by_user[u])
        sessions = []
        start = prev = ts[0]
        cnt = 1
        for t in ts[1:]:
            if t - prev > gap:
                sessions.append((start, prev, cnt))
                start, cnt = t, 0
            cnt += 1
            prev = t
        sessions.append((start, prev, cnt))
        out[u] = sessions
    return out


# ---------- D. Честные выводы ----------

def binom_p(k: int, n: int) -> float:
    """D1. Двусторонний точный тест «монета честная»: k успехов из n. p = min(1, 2·P(X ≤ min(k, n−k))),
    округлить до 4."""
    if not 0 <= k <= n:
        raise ValueError("0 <= k <= n")
    if n == 0:
        return 1.0
    m = min(k, n - k)
    return round(min(1.0, 2 * sum(math.comb(n, i) for i in range(m + 1)) / 2 ** n), 4)


def ab_test(ca: int, na: int, cb: int, nb: int) -> tuple[float, float]:
    """D2. Z-тест двух долей: p = (ca+cb)/(na+nb), se = √(p(1−p)(1/na + 1/nb)), z = (cb/nb − ca/na)/se,
    p_value = erfc(|z|/√2). Ответ — (z, p_value), округлить до 4. se = 0 — (0.0, 1.0)."""
    p = (ca + cb) / (na + nb)
    se = math.sqrt(p * (1 - p) * (1 / na + 1 / nb))
    if se == 0:
        return 0.0, 1.0
    z = (cb / nb - ca / na) / se
    return round(z, 4), round(math.erfc(abs(z) / math.sqrt(2)), 4)


def simpson(groups: dict[str, tuple[int, int, int, int]]) -> dict:
    """D3. Группы: имя → (побед A, партий A, побед B, партий B). Кто лучше по доле побед в каждой группе
    и в сумме ("A", "B" или "tie"; сравнение долей без округления через перекрёстное умножение).
    paradox — в сумме выигрывает одна сторона, а во всех группах (без ничьих) — другая."""
    def better(wa, na, wb, nb):
        x, y = wa * nb, wb * na
        return "A" if x > y else "B" if y > x else "tie"
    by = {g: better(*v) for g, v in groups.items()}
    tot = [sum(v[i] for v in groups.values()) for i in range(4)]
    overall = better(*tot)
    other = {"A": "B", "B": "A"}.get(overall)
    paradox = other is not None and bool(by) and all(w == other for w in by.values())
    return {"overall": overall, "by_group": by, "paradox": paradox}
