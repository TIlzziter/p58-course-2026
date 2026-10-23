"""Контест 7 · Тесты и логи — решения A1–D3."""
import re
import xml.etree.ElementTree as ET
from collections import Counter
from itertools import combinations

# ---------- A. Тесты ----------


def junit_summary(xml: str) -> dict:
    root = ET.fromstring(xml)
    res = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0, "time": 0.0}
    for tc in root.iter("testcase"):
        tags = {c.tag for c in tc}
        key = "failed" if "failure" in tags else "errors" if "error" in tags else "skipped" if "skipped" in tags else "passed"
        res[key] += 1
        res["time"] += float(tc.get("time", 0))
    res["time"] = round(res["time"], 3)
    return res


def flaky(runs: list[dict[str, bool]]) -> list[str]:
    seen: dict[str, set[bool]] = {}
    for run in runs:
        for t, ok in run.items():
            seen.setdefault(t, set()).add(ok)
    return sorted(t for t, s in seen.items() if len(s) == 2)


def missing_ranges(covered: set[int], total: int, skip: set[int] = frozenset()) -> str:
    miss = [i for i in range(1, total + 1) if i not in covered and i not in skip]
    parts, i = [], 0
    while i < len(miss):
        j = i
        while j + 1 < len(miss) and miss[j + 1] == miss[j] + 1:
            j += 1
        parts.append(str(miss[i]) if i == j else f"{miss[i]}-{miss[j]}")
        i = j + 1
    return ", ".join(parts)


def min_tests(kills: dict[str, set[str]]) -> list[str] | None:
    killable = {m for m, ts in kills.items() if ts}
    tests = sorted(set().union(*kills.values())) if kills else []
    for k in range(len(tests) + 1):
        for combo in combinations(tests, k):
            chosen = set(combo)
            if all(kills[m] & chosen for m in killable):
                return list(combo)
    return None


# ---------- B. Логи ----------

ACCESS = re.compile(r'(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] "(?P<method>[A-Z]+) (?P<path>\S+) [^"]*" '
                    r'(?P<status>\d{3}) (?P<bytes>\d+|-) "[^"]*" "(?P<ua>[^"]*)"')


def parse_access(line: str) -> dict | None:
    m = ACCESS.fullmatch(line.strip())
    if not m:
        return None
    d = m.groupdict()
    d["status"] = int(d["status"])
    d["bytes"] = 0 if d["bytes"] == "-" else int(d["bytes"])
    return d


def top_ips(lines, n: int) -> list[tuple[str, int]]:
    c = Counter(r["ip"] for r in map(parse_access, lines) if r)
    return sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[:n]


def trace(records: list[dict], request_id: str) -> list[str]:
    hits = [(r["ts"], i, r) for i, r in enumerate(records) if r.get("rid") == request_id]
    return [f'{r["service"]}: {r["msg"]}' for _, _, r in sorted(hits, key=lambda x: (x[0], x[1]))]


# ---------- C. Метрики ----------


def counter_rate(samples: list[tuple[float, float]]) -> float | None:
    if len(samples) < 2:
        return None
    inc = 0.0
    for (_, a), (_, b) in zip(samples, samples[1:]):
        inc += b - a if b >= a else b          # сброс счётчика: начали с нуля
    return inc / (samples[-1][0] - samples[0][0])


def uptime(checks: list[bool], interval: int) -> tuple[float, int]:
    if not checks:
        raise ValueError("нет проверок")
    longest = run = 0
    for ok in checks:
        run = 0 if ok else run + 1
        longest = max(longest, run)
    return round(100 * sum(checks) / len(checks), 2), longest * interval


def error_budget(total: int, failed: int, slo: float) -> tuple[int, int, float]:
    allowed = int(round(total * (1 - slo), 9))
    left = allowed - failed
    burned = failed / allowed if allowed else (0.0 if failed == 0 else float("inf"))
    return allowed, left, round(burned, 3)


def burn_alert(minutes: list[tuple[int, int]], slo: float, factor: float = 14.4, long: int = 60,
               short: int = 5) -> int | None:
    def burn(lo, hi):
        tot = sum(t for t, _ in minutes[lo:hi])
        err = sum(e for _, e in minutes[lo:hi])
        return (err / tot) / (1 - slo) if tot else 0.0

    for m in range(len(minutes)):
        if burn(max(0, m + 1 - long), m + 1) > factor and burn(max(0, m + 1 - short), m + 1) > factor:
            return m
    return None


# ---------- D. Инциденты ----------


def downtime(intervals: list[tuple[int, int]]) -> tuple[list[tuple[int, int]], int]:
    merged: list[list[int]] = []
    for s, e in sorted(intervals):
        if merged and s <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    return [tuple(x) for x in merged], sum(e - s for s, e in merged)


def dedupe_alerts(alerts: list[tuple[int, str]], window: int) -> list[tuple[int, str]]:
    last: dict[str, int] = {}
    out = []
    for ts, name in sorted(alerts):
        if name not in last or ts - last[name] >= window:
            out.append((ts, name))
            last[name] = ts
    return out


def timeline(events: list[tuple[int, str]]) -> list[str]:
    if not events:
        return []
    ev = sorted(events, key=lambda x: x[0])
    t0 = ev[0][0]
    out = []
    for ts, text in ev:
        d = ts - t0
        h, rest = divmod(d, 3600)
        m, s = divmod(rest, 60)
        stamp = f"{h}:{m:02}:{s:02}" if h else f"{m:02}:{s:02}"
        out.append(f"T+{stamp} {text}")
    return out
