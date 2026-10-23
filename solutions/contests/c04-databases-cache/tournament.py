"""E4 (босс): турнир — расписание по кругу, таблица, швейцарская жеребьёвка."""


def round_robin(players: list[str]) -> list[list[tuple[str, str | None]]]:
    """Метод круга: первый игрок стоит на месте, остальные вращаются. Нечётное число — добавляем None (отдых)."""
    ps = list(players) + ([None] if len(players) % 2 else [])
    n = len(ps)
    rounds = []
    for _ in range(n - 1):
        pairs = []
        for i in range(n // 2):
            a, b = ps[i], ps[n - 1 - i]
            if a is None:
                a, b = b, a
            pairs.append((a, b))
        rounds.append(pairs)
        ps = [ps[0], ps[-1], *ps[1:-1]]
    return rounds


def standings(players: list[str], results: list[tuple[str, str, str]]) -> list[tuple[str, int, int, int, int]]:
    """(имя, очки, победы, ничьи, поражения); победа 3, ничья 1. Порядок: очки ↓, победы ↓, имя ↑."""
    t = {p: [0, 0, 0] for p in players}
    for a, b, res in results:
        if a not in t or b not in t or res not in ("win1", "win2", "draw") or a == b:
            raise ValueError((a, b, res))
        if res == "draw":
            t[a][1] += 1
            t[b][1] += 1
        else:
            w, l = (a, b) if res == "win1" else (b, a)
            t[w][0] += 1
            t[l][2] += 1
    rows = [(p, 3 * w + d, w, d, l) for p, (w, d, l) in t.items()]
    return sorted(rows, key=lambda x: (-x[1], -x[2], x[0]))


def swiss_pairs(order: list[str], played: set[frozenset[str]]) -> list[tuple[str, str]]:
    """Пары тура по порядку таблицы без повторных встреч: первый свободный — с ближайшим, с кем ещё не играл.
    Если так дальше не разбить — перебор с возвратом. Невозможно — ValueError. Число игроков чётное."""
    if len(order) % 2:
        raise ValueError("нечётное число игроков")

    def solve(rest: list[str]) -> list[tuple[str, str]] | None:
        if not rest:
            return []
        a = rest[0]
        for i in range(1, len(rest)):
            b = rest[i]
            if frozenset((a, b)) in played:
                continue
            tail = solve(rest[1:i] + rest[i + 1:])
            if tail is not None:
                return [(a, b), *tail]
        return None

    res = solve(list(order))
    if res is None:
        raise ValueError("нельзя разбить на пары без повторов")
    return res
