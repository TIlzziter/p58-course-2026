"""E4 · босс: мини-язык запросов к логам."""
import re

LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
COND = re.compile(r"([A-Za-z_][\w.]*)(>=|<=|!=|=|>|<)([^\s=<>!]+)")


def parse_query(q: str) -> list[tuple[str, str, object]]:
    out = []
    for tok in q.split():
        m = COND.fullmatch(tok)
        if not m:
            raise ValueError(f"не понимаю условие {tok!r}")
        f, op, v = m.groups()
        if re.fullmatch(r"-?\d+", v):
            v = int(v)
        elif re.fullmatch(r"-?\d+\.\d+", v):
            v = float(v)
        if f == "level" and v not in LEVELS:
            raise ValueError(f"нет уровня {v}")
        out.append((f, op, v))
    return out


def _ok(rec, f, op, v):
    if f not in rec:
        return False
    a = rec[f]
    if f == "level":
        if a not in LEVELS:
            return False
        a, v = LEVELS.index(a), LEVELS.index(v)
    if op in ("=", "!="):
        return (a == v) == (op == "=")
    if isinstance(a, bool) or not isinstance(a, (int, float)) or not isinstance(v, (int, float)):
        return False
    return {">": a > v, ">=": a >= v, "<": a < v, "<=": a <= v}[op]


def run_query(records: list[dict], q: str) -> list[dict]:
    conds = parse_query(q)
    return [r for r in records if all(_ok(r, *c) for c in conds)]


STATS = re.compile(r"(count|avg (\w+)|max (\w+)) by (\w+)")


def stats(records: list[dict], q: str) -> dict:
    filt, _, agg = q.partition("|")
    m = STATS.fullmatch(agg.strip())
    if not m:
        raise ValueError("ожидается: count by F | avg F by G | max F by G")
    field = m.group(2) or m.group(3)
    key = m.group(4)
    groups: dict = {}
    for r in run_query(records, filt):
        if key not in r:
            continue
        if field is None:
            groups.setdefault(r[key], []).append(1)
        elif isinstance(r.get(field), (int, float)):
            groups.setdefault(r[key], []).append(r[field])
    res = {}
    for g in sorted(groups, key=str):
        vals = groups[g]
        if field is None:
            res[g] = len(vals)
        elif m.group(2):
            res[g] = round(sum(vals) / len(vals), 1)
        else:
            res[g] = max(vals)
    return res
