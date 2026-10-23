"""Контест 13 · Надёжность и время — эталонные решения A1–D3."""
import random
import re
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

# ---------- A. Время ----------

_UNITS = {"d": 86400, "h": 3600, "m": 60, "s": 1}


def parse_duration(s: str) -> int:
    """A1. "1h30m", "2d", "45s", "1h 5m" → секунды. Единицы d/h/m/s, по убыванию, каждая не больше раза,
    числа — целые. Иначе (и пустая строка) — ValueError."""
    s = s.replace(" ", "")
    m = re.fullmatch(r"(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?", s)
    if not s or not m:
        raise ValueError(s)
    return sum(int(v) * k for v, k in zip(m.groups(), _UNITS.values()) if v)


def utc_to_local(ts: str, tz: str) -> str:
    """A2. Момент UTC "ГГГГ-ММ-ДДTЧЧ:ММ:ССZ" → местное время зоны tz в ISO с смещением."""
    dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    return dt.astimezone(ZoneInfo(tz)).isoformat()


def local_day_bounds(day: str, tz: str) -> tuple[str, str]:
    """A2. Начало и конец (полуинтервал) местных суток day = "ГГГГ-ММ-ДД" зоны tz — в UTC, "…Z"."""
    z = ZoneInfo(tz)
    d = datetime.strptime(day, "%Y-%m-%d")
    a = d.replace(tzinfo=z).astimezone(timezone.utc)
    b = (d + timedelta(days=1)).replace(tzinfo=z).astimezone(timezone.utc)
    f = "%Y-%m-%dT%H:%M:%SZ"
    return a.strftime(f), b.strftime(f)


def merge_intervals(iv: list[tuple[float, float]]) -> list[tuple[float, float]]:
    out: list[list[float]] = []
    for a, b in sorted(iv):
        if out and a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return [(a, b) for a, b in out]


def uptime(outages: list[tuple[float, float]], start: float, end: float) -> float:
    """A3. Доступность за [start, end) в процентах, 3 знака. Простои (начало, конец) могут пересекаться
    и выходить за границы периода — обрезаем и объединяем."""
    clipped = [(max(a, start), min(b, end)) for a, b in outages if min(b, end) > max(a, start)]
    down = sum(b - a for a, b in merge_intervals(clipped))
    return round(100 * (1 - down / (end - start)), 3)


def _field(spec: str, lo: int, hi: int) -> set[int]:
    out = set()
    for part in spec.split(","):
        if part == "*":
            out |= set(range(lo, hi + 1))
        elif m := re.fullmatch(r"\*/(\d+)", part):
            out |= set(range(lo, hi + 1, int(m.group(1))))
        elif m := re.fullmatch(r"(\d+)-(\d+)", part):
            out |= set(range(int(m.group(1)), int(m.group(2)) + 1))
        else:
            out.add(int(part))
    if not out or min(out) < lo or max(out) > hi:
        raise ValueError(spec)
    return out


def cron_next(expr: str, after: datetime) -> datetime:
    """A4*. Упрощённый cron "минута час * * день_недели": в полях — *, число, список через запятую,
    диапазон a-b и шаг */n; день недели 0–6, 0 = воскресенье (как в cron). Ближайший момент строго после
    after (секунды отбрасываются)."""
    mi, ho, dom, mon, dow = expr.split()
    if dom != "*" or mon != "*":
        raise ValueError("день месяца и месяц не поддерживаются")
    mins, hours, days = _field(mi, 0, 59), _field(ho, 0, 23), _field(dow, 0, 6)
    t = after.replace(second=0, microsecond=0) + timedelta(minutes=1)
    for _ in range(8 * 24 * 60):
        if (t.isoweekday() % 7) in days and t.hour in hours and t.minute in mins:
            return t
        t += timedelta(minutes=1)
    raise ValueError("нет подходящего момента")


# ---------- B. Повторы ----------

def backoff_schedule(n: int, base: float, cap: float, seed: int | None = None) -> list[float]:
    """B1. Паузы перед повторами 1..n: min(cap, base · 2^(i−1)). С seed — «полный джиттер»:
    rng = random.Random(seed), пауза = rng.uniform(0, ту же величину). 3 знака."""
    rng = random.Random(seed) if seed is not None else None
    out = []
    for i in range(n):
        d = min(cap, base * 2 ** i)
        out.append(round(float(rng.uniform(0, d) if rng else d), 3))
    return out


def retry(fn, attempts: int, retry_on: tuple = (Exception,), base: float = 0.1, cap: float = 5.0, sleep=None):
    """B2. Вызвать fn() до attempts раз. Исключение из retry_on — пауза sleep(пауза из B1 без джиттера)
    и снова; другое исключение — пробросить сразу. Успех — (результат, номер попытки). Попытки
    кончились — пробросить последнее исключение. sleep по умолчанию — time.sleep."""
    import time
    sleep = sleep or time.sleep
    pauses = backoff_schedule(attempts - 1, base, cap)
    for i in range(attempts):
        try:
            return fn(), i + 1
        except retry_on:
            if i == attempts - 1:
                raise
            sleep(pauses[i])
    raise ValueError("attempts должно быть ≥ 1")


class Conflict(Exception):
    pass


class IdempotencyStore:
    """B3. Ключ идемпотентности: handle(key, body, fn) — первый раз выполняет fn(body) и запоминает ответ;
    повтор с тем же key и тем же body — тот же ответ без вызова fn; тот же key с другим body — Conflict.
    Если fn упала — ничего не запоминаем. Ключ живёт ttl секунд от первого успешного вызова (now — параметр)."""

    def __init__(self, ttl: float = 86400):
        self.ttl = ttl
        self.data: dict[str, tuple[float, object, object]] = {}

    def handle(self, key: str, body, fn, now: float = 0.0):
        if key in self.data:
            t, b, resp = self.data[key]
            if now - t < self.ttl:
                if b != body:
                    raise Conflict(key)
                return resp
            del self.data[key]
        resp = fn(body)
        self.data[key] = (now, body, resp)
        return resp


# ---------- C. Надёжность ----------

def availability(spec) -> float:
    """C1. Доступность системы: число — компонент; ("series", [...]) — все нужны (произведение);
    ("parallel", [...]) — хватит одного (1 − произведение отказов). 6 знаков."""
    def go(s):
        if isinstance(s, (int, float)):
            return float(s)
        kind, parts = s
        vals = [go(p) for p in parts]
        prod = 1.0
        if kind == "series":
            for v in vals:
                prod *= v
            return prod
        if kind == "parallel":
            for v in vals:
                prod *= 1 - v
            return 1 - prod
        raise ValueError(kind)
    return round(go(spec), 6)


def downtime_budget(slo_percent: float, days: int = 30) -> float:
    """C2. Допустимый простой за days суток при доступности slo_percent, минуты, 1 знак."""
    return round(days * 24 * 60 * (1 - slo_percent / 100), 1)


def incident_stats(outages: list[tuple[float, float]], start: float, end: float) -> dict:
    """C3. Простои в секундах (пересекающиеся — один инцидент). {"count", "mttr_min" — средняя длительность,
    минуты, 1 знак, "mtbf_h" — (длина периода − простой) / count, часы, 1 знак}. Нет инцидентов — mttr 0.0,
    mtbf — None."""
    m = merge_intervals([(max(a, start), min(b, end)) for a, b in outages if min(b, end) > max(a, start)])
    if not m:
        return {"count": 0, "mttr_min": 0.0, "mtbf_h": None}
    down = sum(b - a for a, b in m)
    return {"count": len(m), "mttr_min": round(down / len(m) / 60, 1),
            "mtbf_h": round((end - start - down) / len(m) / 3600, 1)}


def health_transitions(checks: list[bool], fail_after: int = 3, recover_after: int = 2) -> list[tuple[int, str]]:
    """C4*. Проверки здоровья по порядку (True — ответил). Сначала "up". В "down" — после fail_after неудач
    подряд, обратно в "up" — после recover_after удач подряд. Ответ — (индекс проверки, новое состояние)."""
    state, run, out = "up", 0, []
    for i, ok in enumerate(checks):
        bad = not ok
        if (state == "up") == bad:
            run += 1
        else:
            run = 0
        if state == "up" and run >= fail_after:
            state, run = "down", 0
            out.append((i, state))
        elif state == "down" and run >= recover_after:
            state, run = "up", 0
            out.append((i, state))
    return out


# ---------- D. Время в распределённой системе ----------

def lamport(events: list[tuple]) -> list[int]:
    """D1. Часы Лэмпорта. Событие: (процесс, "local") | (процесс, "send", id) | (процесс, "recv", id).
    local/send: часы += 1; recv: часы = max(часы, метка сообщения) + 1. Ответ — метка каждого события."""
    clock: dict[str, int] = {}
    sent: dict[str, int] = {}
    out = []
    for e in events:
        p, kind = e[0], e[1]
        c = clock.get(p, 0)
        if kind == "recv":
            c = max(c, sent[e[2]]) + 1
        else:
            c += 1
            if kind == "send":
                sent[e[2]] = c
        clock[p] = c
        out.append(c)
    return out


def vc_compare(a: dict[str, int], b: dict[str, int]) -> str:
    """D2. Векторные часы (нет ключа — 0): "equal", "before" (a ≤ b везде и где-то <), "after", "concurrent"."""
    keys = a.keys() | b.keys()
    le = all(a.get(k, 0) <= b.get(k, 0) for k in keys)
    ge = all(a.get(k, 0) >= b.get(k, 0) for k in keys)
    return "equal" if le and ge else "before" if le else "after" if ge else "concurrent"


def lww_merge(*replicas: dict[str, tuple[int, str, object]]) -> dict[str, object]:
    """D3. Регистр «последняя запись побеждает»: ключ → (время, узел, значение). Побеждает большее время,
    при равенстве — больший узел (строки). Ответ — ключ → значение, ключи по алфавиту."""
    best: dict[str, tuple] = {}
    for r in replicas:
        for k, v in r.items():
            if k not in best or v[:2] > best[k][:2]:
                best[k] = v
    return {k: best[k][2] for k in sorted(best)}
