"""Контест 11 · E4 босс: случайность в дереве игры — expectimax и «Свинья»."""
from fractions import Fraction
from functools import cache


def expectimax(node) -> Fraction:
    """а) Узел — число (лист) или пара (тип, дети): "max", "min" или "chance"; у "chance" дети — пары
    (вероятность, узел), вероятности — Fraction или int. Ответ — Fraction."""
    if isinstance(node, int | Fraction):
        return Fraction(node)
    kind, kids = node
    if kind == "max":
        return max(expectimax(k) for k in kids)
    if kind == "min":
        return min(expectimax(k) for k in kids)
    if kind == "chance":
        if sum(Fraction(p) for p, _ in kids) != 1:
            raise ValueError("сумма вероятностей ≠ 1")
        return sum((Fraction(p) * expectimax(k) for p, k in kids), Fraction(0))
    raise ValueError(kind)


def reach_probability(target: int) -> Fraction:
    """б) «Свинья»: бросаем кубик, 1 — ход сгорает (0 очков), 2..6 — прибавляются. Бросаем, пока не наберём
    ≥ target. Вероятность успеть, Fraction."""
    @cache
    def p(s):
        if s >= target:
            return Fraction(1)
        return sum((p(s + d) for d in range(2, 7)), Fraction(0)) / 6
    return p(0)


def expected_hold(k: int) -> Fraction:
    """в) Ожидаемые очки за ход при стратегии «бросать, пока сумма < k, затем остановиться»."""
    @cache
    def e(s):
        if s >= k:
            return Fraction(s)
        return sum((e(s + d) for d in range(2, 7)), Fraction(0)) / 6
    return e(0)


def best_hold(limit: int = 100) -> list[int]:
    """в) Все k из 1..limit с наибольшим expected_hold(k), по возрастанию."""
    vals = {k: expected_hold(k) for k in range(1, limit + 1)}
    m = max(vals.values())
    return [k for k, v in vals.items() if v == m]
