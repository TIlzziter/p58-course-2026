"""Журнал нагрузочного теста → статистика по эндпоинтам (задачи 1–3)."""
import csv
import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Request:
    ts: float      # секунды от начала теста
    name: str      # эндпоинт, например "GET /api/rooms"
    status: int    # HTTP-статус; 0 — соединение не удалось
    ms: float      # время ответа, мс


def load_log(path) -> tuple[list[Request], int]:
    """Задача 1. CSV с колонками ts,name,status,ms. Строки, которые не разбираются (не хватает полей,
    не число, отрицательное время), пропускаем и считаем. Ответ — (запросы по возрастанию ts, пропущено)."""
    out, skipped = [], 0
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                r = Request(float(row["ts"]), row["name"].strip(), int(row["status"]), float(row["ms"]))
            except (TypeError, ValueError, KeyError, AttributeError):
                skipped += 1
                continue
            if r.ms < 0 or r.ts < 0 or not r.name:
                skipped += 1
                continue
            out.append(r)
    out.sort(key=lambda r: r.ts)
    return out, skipped


def percentile(values: list[float], p: float) -> float:
    """Задача 2. Перцентиль методом ближайшего ранга: элемент номер ceil(p/100 · n) (с 1) в сортировке."""
    if not values:
        raise ValueError("пусто")
    s = sorted(values)
    k = max(1, math.ceil(p / 100 * len(s)))
    return s[k - 1]


def is_failure(r: Request) -> bool:
    return r.status == 0 or r.status >= 500


def endpoint_stats(reqs: list[Request]) -> dict[str, dict]:
    """Задача 2. По каждому эндпоинту (ключи по алфавиту): count, failures (статус 0 или ≥ 500),
    fail_rate (доля, 4 знака), rps (count / длительность всего теста, 2 знака; длительность — max ts − min ts,
    если 0 — 1 с), p50, p95, p99, max — по времени ответа всех запросов эндпоинта."""
    if not reqs:
        return {}
    duration = (max(r.ts for r in reqs) - min(r.ts for r in reqs)) or 1.0
    groups: dict[str, list[Request]] = {}
    for r in reqs:
        groups.setdefault(r.name, []).append(r)
    out = {}
    for name in sorted(groups):
        g = groups[name]
        ms = [r.ms for r in g]
        fails = sum(is_failure(r) for r in g)
        out[name] = {
            "count": len(g), "failures": fails, "fail_rate": round(fails / len(g), 4),
            "rps": round(len(g) / duration, 2),
            "p50": percentile(ms, 50), "p95": percentile(ms, 95), "p99": percentile(ms, 99), "max": max(ms),
        }
    return out


def compare(before: dict, after: dict, threshold: float = 0.1) -> list[dict]:
    """Задача 3. Для эндпоинтов из обоих замеров (по алфавиту): p95 до и после, change = (после − до) / до
    (3 знака), verdict: "хуже", если change > threshold или fail_rate вырос больше чем на 0.01;
    иначе "лучше", если change < −threshold; иначе "без изменений"."""
    rows = []
    for name in sorted(before.keys() & after.keys()):
        b, a = before[name], after[name]
        change = round((a["p95"] - b["p95"]) / b["p95"], 3)
        if change > threshold or a["fail_rate"] - b["fail_rate"] > 0.01:
            verdict = "хуже"
        elif change < -threshold:
            verdict = "лучше"
        else:
            verdict = "без изменений"
        rows.append({"name": name, "p95_before": b["p95"], "p95_after": a["p95"], "change": change,
                     "fail_before": b["fail_rate"], "fail_after": a["fail_rate"], "verdict": verdict})
    return rows


def render_markdown(rows: list[dict]) -> str:
    """Задача 3. Таблица Markdown:
    | Эндпоинт | p95 до, мс | p95 после, мс | Изменение | Ошибки до | Ошибки после | Вывод |
    Изменение — со знаком и процентом без дробной части (+12 %, −40 %, 0 %; минус — U+2212), ошибки —
    в процентах с одним знаком (0.5 %). Числа p95 — как есть (int, если целое)."""
    def num(x):
        return int(x) if float(x).is_integer() else x

    def pct(x):
        v = round(x * 100)
        return f"+{v} %" if v > 0 else f"\u2212{-v} %" if v < 0 else "0 %"

    lines = ["| Эндпоинт | p95 до, мс | p95 после, мс | Изменение | Ошибки до | Ошибки после | Вывод |",
             "|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['name']} | {num(r['p95_before'])} | {num(r['p95_after'])} | {pct(r['change'])} | "
                     f"{r['fail_before'] * 100:.1f} % | {r['fail_after'] * 100:.1f} % | {r['verdict']} |")
    return "\n".join(lines)
