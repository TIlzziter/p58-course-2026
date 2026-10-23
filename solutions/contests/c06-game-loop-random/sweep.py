"""E5*: время первого касания движущегося прямоугольника с неподвижным."""
from fractions import Fraction


def time_of_impact(a, v, b):
    t_enter, t_exit = Fraction(-10**18), Fraction(10**18)
    for s, size, d, lo, bsize in ((a[0], a[2], v[0], b[0], b[2]), (a[1], a[3], v[1], b[1], b[3])):
        # касание по оси: s + d·t ∈ [lo − size, lo + bsize]
        left, right = lo - size, lo + bsize
        if d == 0:
            if not left <= s <= right:
                return None
            continue
        t1, t2 = Fraction(left - s, d), Fraction(right - s, d)
        if t1 > t2:
            t1, t2 = t2, t1
        t_enter, t_exit = max(t_enter, t1), min(t_exit, t2)
    if t_enter > t_exit or t_exit < 0 or t_enter > 1:
        return None
    return float(max(t_enter, Fraction(0)))
