"""Журнал нагрузочного теста → статистика по эндпоинтам (задачи 1–3)."""
import csv
import math  # noqa: F401
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
            # TODO: битые строки пропускать и считать; отрицательные ms/ts и пустое имя — тоже битые
            out.append(Request(float(row["ts"]), row["name"], int(row["status"]), float(row["ms"])))
    # TODO: отсортировать по ts
    return out, skipped


def percentile(values: list[float], p: float) -> float:
    """Задача 2. Перцентиль методом ближайшего ранга: элемент номер ceil(p/100 · n) (с 1) в сортировке."""
    if not values:
        raise ValueError("пусто")
    s = sorted(values)
    return s[int(p / 100 * len(s))]  # BUG: это не ближайший ранг, и p = 100 падает


def is_failure(r: Request) -> bool:
    return r.status == 0 or r.status >= 500


def endpoint_stats(reqs: list[Request]) -> dict[str, dict]:
    """Задача 2. По каждому эндпоинту (ключи по алфавиту): count, failures (статус 0 или ≥ 500),
    fail_rate (доля, 4 знака), rps (count / длительность всего теста, 2 знака; длительность — max ts − min ts,
    если 0 — 1 с), p50, p95, p99, max — по времени ответа всех запросов эндпоинта."""
    # TODO
    raise NotImplementedError


def compare(before: dict, after: dict, threshold: float = 0.1) -> list[dict]:
    """Задача 3. Для эндпоинтов из обоих замеров (по алфавиту): p95 до и после, change = (после − до) / до
    (3 знака), verdict: "хуже", если change > threshold или fail_rate вырос больше чем на 0.01;
    иначе "лучше", если change < −threshold; иначе "без изменений"."""
    # TODO
    raise NotImplementedError


def render_markdown(rows: list[dict]) -> str:
    """Задача 3. Таблица Markdown:
    | Эндпоинт | p95 до, мс | p95 после, мс | Изменение | Ошибки до | Ошибки после | Вывод |
    Изменение — со знаком и процентом без дробной части (+12 %, −40 %, 0 %; минус — U+2212), ошибки —
    в процентах с одним знаком (0.5 %). Числа p95 — как есть (int, если целое)."""
    # TODO
    raise NotImplementedError
