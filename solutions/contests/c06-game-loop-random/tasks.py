"""Контест 6 · Игровой цикл и рандом — решения A1–D3."""
from bisect import bisect_right
from collections import Counter
from fractions import Fraction
from itertools import accumulate, combinations, product
from math import floor

# ---------- A. Рандом ----------

def fisher_yates_trace(n, rolls):
    a = list(range(n))
    if len(rolls) != max(n - 1, 0):
        raise ValueError("нужно n − 1 бросков")
    for i, j in zip(range(n - 1, 0, -1), rolls):
        if not 0 <= j <= i:
            raise ValueError(f"бросок {j} вне 0..{i}")
        a[i], a[j] = a[j], a[i]
    return a


def weighted_pick(weights, r):
    names = list(weights)
    bounds = list(accumulate(weights[k] for k in names))
    if not bounds or not 0 <= r < bounds[-1]:
        raise ValueError("r вне диапазона")
    return names[bisect_right(bounds, r)]


def lcg(seed, n, a=1103515245, c=12345, m=2**31):
    out, x = [], seed
    for _ in range(n):
        x = (a * x + c) % m
        out.append(x)
    return out


def naive_shuffle_counts(n):
    cnt = Counter()
    for rolls in product(range(n), repeat=n):
        a = list(range(n))
        for i, j in enumerate(rolls):
            a[i], a[j] = a[j], a[i]
        cnt[tuple(a)] += 1
    return dict(sorted(cnt.items()))


# ---------- B. Автоматы ----------

def run_fsm(trans, start, events):
    state, ignored = start, 0
    for e in events:
        if (state, e) in trans:
            state = trans[(state, e)]
        else:
            ignored += 1
    return state, ignored


def _graph(trans):
    g = {}
    for (s, _), t in trans.items():
        g.setdefault(s, set()).add(t)
    return g


def reachable(trans, start):
    g, seen, stack = _graph(trans), {start}, [start]
    while stack:
        for t in g.get(stack.pop(), ()):
            if t not in seen:
                seen.add(t)
                stack.append(t)
    return sorted(seen)


def dead_states(trans, start, finals):
    return sorted(s for s in reachable(trans, start) if not set(reachable(trans, s)) & set(finals))


# ---------- C. Столкновения ----------

def _overlap(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah


def aabb_pairs(boxes):
    return [(p, q) for p, q in combinations(sorted(boxes), 2) if _overlap(boxes[p], boxes[q])]


def circle_pairs(circles):
    res = []
    for p, q in combinations(sorted(circles), 2):
        (x1, y1, r1), (x2, y2, r2) = circles[p], circles[q]
        if (x1 - x2) ** 2 + (y1 - y2) ** 2 <= (r1 + r2) ** 2:
            res.append((p, q))
    return res


def segment_hits_rect(p, q, rect):
    """Лианг — Барски на дробях: отрезок p→q и замкнутый прямоугольник."""
    x, y, w, h = rect
    t0, t1 = Fraction(0), Fraction(1)
    dx, dy = q[0] - p[0], q[1] - p[1]
    for d, lo, hi, s in ((dx, x, x + w, p[0]), (dy, y, y + h, p[1])):
        if d == 0:
            if not lo <= s <= hi:
                return False
            continue
        a, b = Fraction(lo - s, d), Fraction(hi - s, d)
        if a > b:
            a, b = b, a
        t0, t1 = max(t0, a), min(t1, b)
        if t0 > t1:
            return False
    return True


def _cells(box, cell):
    x, y, w, h = box
    return {(i, j) for i in range(floor(x / cell), floor((x + w) / cell) + 1)
            for j in range(floor(y / cell), floor((y + h) / cell) + 1)}


def spatial_hash_pairs(boxes, cell):
    grid = {}
    for name, b in boxes.items():
        for c in _cells(b, cell):
            grid.setdefault(c, []).append(name)
    cand = {tuple(sorted(pq)) for names in grid.values() for pq in combinations(names, 2)}
    pairs = sorted(pq for pq in cand if _overlap(boxes[pq[0]], boxes[pq[1]]))
    return pairs, len(cand)


# ---------- D. Время и углы ----------

def lerp_angle(a, b, t):
    d = (b - a) % 360
    if d > 180:
        d -= 360
    return (a + d * t) % 360


def fixed_steps(frame_times, step, max_steps):
    out, acc = [], 0
    for prev, cur in zip(frame_times, frame_times[1:]):
        acc += cur - prev
        k = acc // step
        if k > max_steps:
            k, acc = max_steps, acc % step
        else:
            acc -= k * step
        out.append(int(k))
    return out


def frame_stats(frame_times):
    dts = [b - a for a, b in zip(frame_times, frame_times[1:])]
    if not dts:
        raise ValueError("нужно хотя бы два кадра")
    s = sorted(dts)
    med = s[(len(s) - 1) // 2]
    fps = round(1000 * len(dts) / (frame_times[-1] - frame_times[0]))
    return fps, max(dts), sum(dt > 2 * med for dt in dts)
