"""Контест 10 · E4 босс: A/B-эксперимент от распределения до решения."""
import hashlib
import math

from tasks import ab_test


def assign(user_id: int, experiment: str, variants: list[str], weights: list[int]) -> str:
    """а) Детерминированное распределение: h = sha256(f"{experiment}:{user_id}"), bucket = int(первые 8 hex, 16)
    % 100; веса в процентах (сумма 100) делят 0..99 на отрезки по порядку."""
    if sum(weights) != 100 or len(weights) != len(variants):
        raise ValueError("веса")
    bucket = int(hashlib.sha256(f"{experiment}:{user_id}".encode()).hexdigest()[:8], 16) % 100
    acc = 0
    for v, w in zip(variants, weights, strict=True):
        acc += w
        if bucket < acc:
            return v
    raise AssertionError


def chi2_sf(x: float, df: int) -> float:
    """Хвост распределения хи-квадрат для df = 1 или 2."""
    if df == 1:
        return math.erfc(math.sqrt(x / 2))
    if df == 2:
        return math.exp(-x / 2)
    raise ValueError("df 1 или 2")


def srm_check(counts: list[int], weights: list[int]) -> float:
    """б) Sample ratio mismatch: χ² = Σ (наблюдали − ждали)² / ждали, ждали = всего · вес/100; df = вариантов − 1
    (2 или 3 варианта). Ответ — p-value, округлить до 4."""
    total = sum(counts)
    chi2 = sum((c - total * w / 100) ** 2 / (total * w / 100) for c, w in zip(counts, weights, strict=True))
    return round(chi2_sf(chi2, len(counts) - 1), 4)


def report(users: list[int], converted: set[int], experiment: str, weights=(50, 50)) -> dict:
    """в) Два варианта "control", "test". Распределить users через а), посчитать n и конверсии по вариантам,
    srm через б), z и p через D2 (control — A, test — B), lift = rate_test − rate_control (округлить до 4).
    decision: srm < 0.01 → "broken"; иначе p < 0.05 → "ship" при lift > 0 и "rollback" при lift < 0;
    иначе "wait"."""
    names = ["control", "test"]
    n = dict.fromkeys(names, 0)
    c = dict.fromkeys(names, 0)
    for u in users:
        v = assign(u, experiment, names, list(weights))
        n[v] += 1
        c[v] += u in converted
    srm = srm_check([n["control"], n["test"]], list(weights))
    z, p = ab_test(c["control"], n["control"], c["test"], n["test"])
    rate = {v: c[v] / n[v] if n[v] else 0.0 for v in names}
    lift = round(rate["test"] - rate["control"], 4)
    if srm < 0.01:
        decision = "broken"
    elif p < 0.05:
        decision = "ship" if lift > 0 else "rollback"
    else:
        decision = "wait"
    return {"n": n, "conv": c, "srm_p": srm, "z": z, "p": p, "lift": lift, "decision": decision}
