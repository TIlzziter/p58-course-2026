"""E4 · босс: запись и проверка повторов."""


def rle_encode(inputs):
    out = []
    for v in inputs:
        if out and out[-1][0] == v:
            out[-1][1] += 1
        else:
            out.append([v, 1])
    return out


def rle_decode(runs):
    res = []
    for v, k in runs:
        if k <= 0:
            raise ValueError("длина серии должна быть > 0")
        res.extend([v] * k)
    return res


def delta(prev, cur):
    return {"set": {k: v for k, v in cur.items() if k not in prev or prev[k] != v},
            "del": sorted(k for k in prev if k not in cur)}


def apply_delta(state, d):
    new = {k: v for k, v in state.items() if k not in d["del"]}
    new.update(d["set"])
    return new


def first_desync(n, check):
    """check(i) — совпадают ли хэши на тике i; True … True False … False. Первый False или None."""
    lo, hi = 0, n          # ответ в [lo, hi]; hi == n значит «нет расхождения»
    while lo < hi:
        mid = (lo + hi) // 2
        if check(mid):
            lo = mid + 1
        else:
            hi = mid
    return None if lo == n else lo
