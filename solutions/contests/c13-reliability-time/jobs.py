"""Контест 13 · E4 босс: очередь задач с повторами и ровно-однократным эффектом."""
import heapq


def next_attempt_at(fail_time: float, attempt: int, base: float = 1.0, cap: float = 60.0) -> float:
    """а) После неудачной попытки номер attempt (с 1) в момент fail_time — следующая через
    min(cap, base · 2^(attempt − 1))."""
    return fail_time + min(cap, base * 2 ** (attempt - 1))


def simulate(jobs: dict[str, tuple[float, list[bool]]], max_attempts: int = 4, base: float = 1.0,
             cap: float = 60.0) -> dict[str, tuple[str, int, float]]:
    """б) Задача: id → (время постановки, исходы попыток по порядку; если список кончился — дальше
    неудачи). Попытки мгновенны, обработчиков сколько угодно. Ответ: id → ("done" | "dead", попыток,
    время последней попытки). "dead" — после max_attempts неудач (dead letter)."""
    res = {}
    for jid, (t, outcomes) in jobs.items():
        for attempt in range(1, max_attempts + 1):
            ok = outcomes[attempt - 1] if attempt <= len(outcomes) else False
            if ok:
                res[jid] = ("done", attempt, t)
                break
            if attempt == max_attempts:
                res[jid] = ("dead", attempt, t)
                break
            t = next_attempt_at(t, attempt, base, cap)
    return res


def timeline(jobs: dict[str, tuple[float, list[bool]]], **kw) -> list[tuple[float, str, int]]:
    """б) Все попытки всех задач по времени: (время, id, номер попытки), при равенстве — по id."""
    max_attempts = kw.get("max_attempts", 4)
    base, cap = kw.get("base", 1.0), kw.get("cap", 60.0)
    heap = [(t, jid, 1) for jid, (t, _) in jobs.items()]
    heapq.heapify(heap)
    out = []
    while heap:
        t, jid, a = heapq.heappop(heap)
        out.append((t, jid, a))
        outcomes = jobs[jid][1]
        ok = outcomes[a - 1] if a <= len(outcomes) else False
        if not ok and a < max_attempts:
            heapq.heappush(heap, (next_attempt_at(t, a, base, cap), jid, a + 1))
    return out


def apply_rewards(deliveries: list[tuple[str, str, int]]) -> dict[str, int]:
    """в) Доставка «хотя бы один раз»: (id события, игрок, монеты) может прийти повторно. Начислить каждое
    событие один раз; одинаковый id с другим содержимым — ValueError. Ответ — баланс игроков по алфавиту."""
    seen: dict[str, tuple[str, int]] = {}
    bal: dict[str, int] = {}
    for eid, player, coins in deliveries:
        if eid in seen:
            if seen[eid] != (player, coins):
                raise ValueError(eid)
            continue
        seen[eid] = (player, coins)
        bal[player] = bal.get(player, 0) + coins
    return dict(sorted(bal.items()))
