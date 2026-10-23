"""Контест 12 · Нагрузка и масштаб — эталонные решения A1–D3."""
import asyncio
import bisect
import hashlib
import heapq
import math
import re
from collections import Counter, OrderedDict

# ---------- A. Метрики ----------

def rps_series(timestamps: list[float]) -> list[int]:
    """A1. Запросов в каждую секунду [s, s+1) от 0 до последней непустой секунды включительно."""
    if not timestamps:
        return []
    out = [0] * (int(max(timestamps)) + 1)
    for t in timestamps:
        out[int(t)] += 1
    return out


def apdex(latencies: list[float], t: float) -> float:
    """A2. Apdex: довольны (≤ T), терпят (≤ 4T), остальные недовольны; (довольны + терпят / 2) / N, 2 знака."""
    if not latencies:
        raise ValueError("пусто")
    s = sum(x <= t for x in latencies)
    tol = sum(t < x <= 4 * t for x in latencies)
    return round((s + tol / 2) / len(latencies), 2)


def error_budget(errors: int, total: int, slo: float = 0.999) -> dict:
    """A3. Бюджет ошибок: разрешено (1 − slo) · total ошибок (округлить вниз), burn = errors / разрешено
    (2 знака, при разрешено = 0 — inf, если ошибки есть, иначе 0.0), left = разрешено − errors (не меньше 0)."""
    allowed = math.floor((1 - slo) * total + 1e-9)
    if allowed == 0:
        burn = math.inf if errors else 0.0
    else:
        burn = round(errors / allowed, 2)
    return {"allowed": allowed, "burn": burn, "left": max(0, allowed - errors)}


def hist_percentile(buckets: list[tuple[float, int]], p: float) -> float:
    """A4*. Гистограмма: (верхняя граница, сколько запросов) по возрастанию границ. Оценка перцентиля —
    граница первой корзины, где накопленная доля ≥ p / 100. Пусто — ValueError."""
    total = sum(c for _, c in buckets)
    if total == 0:
        raise ValueError("пусто")
    acc = 0
    for bound, c in buckets:
        acc += c
        if acc * 100 >= p * total:
            return bound
    return buckets[-1][0]


# ---------- B. Очереди ----------

def mm1(lam: float, mu: float) -> dict:
    """B1. Очередь M/M/1: ρ = λ/μ; L = ρ/(1 − ρ) — в системе в среднем; W = 1/(μ − λ) — время в системе, мс.
    3 знака. ρ ≥ 1 — ValueError."""
    rho = lam / mu
    if rho >= 1:
        raise ValueError("очередь растёт бесконечно")
    return {"rho": round(rho, 3), "L": round(rho / (1 - rho), 3), "W_ms": round(1000 / (mu - lam), 3)}


def queue_waits(arrivals: list[float], service: list[float], workers: int) -> list[float]:
    """B2. Очередь FIFO с workers обработчиками: запрос i приходит в arrivals[i] (по возрастанию) и
    обрабатывается service[i]. Сколько каждый ждал до начала обработки."""
    free = [0.0] * workers
    heapq.heapify(free)
    waits = []
    for a, s in zip(arrivals, service, strict=True):
        f = heapq.heappop(free)
        start = max(a, f)
        waits.append(start - a)
        heapq.heappush(free, start + s)
    return waits


def token_bucket(rate: float, capacity: float, times: list[float]) -> list[bool]:
    """B3. Ведро токенов: в начале (t = 0) полное; копится rate токенов в секунду, не больше capacity.
    Запрос в момент t (по возрастанию) пропускаем, если токенов ≥ 1, и тратим один."""
    tokens, last = capacity, 0.0
    out = []
    for t in times:
        tokens = min(capacity, tokens + (t - last) * rate)
        last = t
        if tokens >= 1 - 1e-9:
            tokens -= 1
            out.append(True)
        else:
            out.append(False)
    return out


# ---------- C. Распределение и кэш ----------

def moved_mod(keys: list[int], n1: int, n2: int) -> float:
    """C1. Шардирование key % n: какая доля ключей сменит шард при переходе от n1 к n2 шардам (3 знака)."""
    return round(sum(k % n1 != k % n2 for k in keys) / len(keys), 3)


def _h(s: str) -> int:
    return int(hashlib.md5(s.encode()).hexdigest()[:8], 16)


class Ring:
    """C2. Согласованное хэширование: у каждого узла vnodes точек _h(f"{узел}#{i}"), i = 0..vnodes−1.
    Ключ — на первый узел по часовой: первая точка ≥ _h(ключ), после последней — снова первая."""

    def __init__(self, nodes: list[str], vnodes: int = 50):
        self.points = sorted((_h(f"{n}#{i}"), n) for n in nodes for i in range(vnodes))
        self.hashes = [p for p, _ in self.points]

    def node(self, key: str) -> str:
        i = bisect.bisect_left(self.hashes, _h(key))
        return self.points[i % len(self.points)][1]


def lru_hits(capacity: int, requests: list[str]) -> tuple[int, list[str]]:
    """C3. Кэш LRU на capacity ключей: (число попаданий, ключи в кэше от давних к свежим в конце)."""
    cache: OrderedDict[str, None] = OrderedDict()
    hits = 0
    for k in requests:
        if k in cache:
            hits += 1
            cache.move_to_end(k)
        else:
            cache[k] = None
            if len(cache) > capacity:
                cache.popitem(last=False)
    return hits, list(cache)


class SingleFlight:
    """C4*. Защита от «набега» на кэш: одновременные get(key) с одним ключом вызывают fetch(key) один раз
    и получают один результат (или одно исключение). Следующий get после завершения — снова fetch."""

    def __init__(self, fetch):
        self.fetch = fetch
        self.inflight: dict[str, asyncio.Future] = {}

    async def get(self, key: str):
        if key in self.inflight:
            return await asyncio.shield(self.inflight[key])
        fut = asyncio.get_running_loop().create_future()
        self.inflight[key] = fut
        try:
            res = await self.fetch(key)
            fut.set_result(res)
            return res
        except Exception as e:
            fut.set_exception(e)
            raise
        finally:
            del self.inflight[key]
            if fut.done() and not fut.cancelled():
                fut.exception()  # пометить как полученное


# ---------- D. База ----------

def n_plus_one(queries: list[str], threshold: int = 3) -> list[tuple[str, int]]:
    """D1. SQL одного запроса к API. Шаблон: строки в '…' → ?, числа → ?, пробелы схлопнуть. Шаблоны,
    встречающиеся ≥ threshold раз: (шаблон, сколько) по убыванию числа, при равенстве — по шаблону."""
    def norm(q):
        q = re.sub(r"'(?:[^']|'')*'", "?", q)
        q = re.sub(r"\b\d+(?:\.\d+)?\b", "?", q)
        return re.sub(r"\s+", " ", q).strip()
    c = Counter(norm(q) for q in queries)
    return sorted(((t, n) for t, n in c.items() if n >= threshold), key=lambda x: (-x[1], x[0]))


def pool_size(rps: float, queries_per_request: float, query_ms: float, headroom: float = 0.3) -> int:
    """D2. Соединений в пуле одной реплики: ceil(rps · запросов_на_запрос · query_ms / 1000 / (1 − headroom))."""
    return math.ceil(rps * queries_per_request * query_ms / 1000 / (1 - headroom) - 1e-9)


def max_replicas(max_connections: int, pool: int, reserved: int = 10) -> int:
    """D2. Сколько реплик выдержит PostgreSQL: (max_connections − reserved) // pool."""
    return (max_connections - reserved) // pool


def pick_index(where_eq: set[str], order_by: str | None, indexes: dict[str, tuple[str, ...]]) -> str | None:
    """D3. Правило левого префикса: индекс полезен, если его первые колонки (≥ 1) — из where_eq. Оценка —
    (длина такого префикса, 1 если следующая колонка индекса — order_by, иначе 0). Лучший — с наибольшей
    оценкой, при равенстве — с меньшим числом колонок, затем по имени. Ни один не полезен — None."""
    best, best_key = None, None
    for name, cols in indexes.items():
        k = 0
        while k < len(cols) and cols[k] in where_eq:
            k += 1
        if k == 0:
            continue
        sort_ok = int(order_by is not None and k < len(cols) and cols[k] == order_by)
        key = (-k, -sort_ok, len(cols), name)
        if best_key is None or key < best_key:
            best, best_key = name, key
    return best
