"""Контест 14 · E4 босс: турнир финала."""
from tasks import elo


def round_robin(players: list[str]) -> list[list[tuple[str, str]]]:
    """а) Круговой турнир методом «карусели»: нечётное число — добавить "BYE" (пары с ним не выводим).
    Первый игрок неподвижен, остальные сдвигаются по кругу на одну позицию каждый тур (последний
    становится вторым). Тур — пары (p[i], p[n−1−i]) для i < n/2."""
    p = list(players)
    if len(p) % 2:
        p.append("BYE")
    n = len(p)
    rounds = []
    for _ in range(n - 1):
        pairs = [(p[i], p[n - 1 - i]) for i in range(n // 2)]
        rounds.append([(a, b) for a, b in pairs if "BYE" not in (a, b)])
        p = [p[0], p[-1], *p[1:-1]]
    return rounds


def standings(results: list[tuple[str, str, float]]) -> list[tuple[str, int]]:
    """б) Результаты (a, b, очки a: 1, 0.5, 0). Победа — 3, ничья — 1, поражение — 0. Таблица по убыванию
    очков; при равенстве двух и более — по очкам в личных встречах только между ними, затем по имени."""
    pts: dict[str, int] = {}
    for a, b, s in results:
        pts.setdefault(a, 0)
        pts.setdefault(b, 0)
        pts[a] += {1: 3, 0.5: 1, 0: 0}[s]
        pts[b] += {1: 0, 0.5: 1, 0: 3}[s]

    def h2h(group: set[str]) -> dict[str, int]:
        h = dict.fromkeys(group, 0)
        for a, b, s in results:
            if a in group and b in group:
                h[a] += {1: 3, 0.5: 1, 0: 0}[s]
                h[b] += {1: 0, 0.5: 1, 0: 3}[s]
        return h

    by_pts: dict[int, set[str]] = {}
    for p, v in pts.items():
        by_pts.setdefault(v, set()).add(p)
    key = {}
    for v, group in by_pts.items():
        h = h2h(group)
        for p in group:
            key[p] = (-v, -h[p], p)
    return [(p, pts[p]) for p in sorted(pts, key=key.get)]


def elo_replay(start: dict[str, int], results: list[tuple[str, str, float]], k: float = 32) -> dict[str, int]:
    """в) Прогнать результаты по порядку через elo (A1); новичок — 1200. Ответ по алфавиту."""
    r = dict(start)
    for a, b, s in results:
        r.setdefault(a, 1200)
        r.setdefault(b, 1200)
        r[a], r[b] = elo(r[a], r[b], s, k)
    return dict(sorted(r.items()))
