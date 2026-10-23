"""Контест 11 · Деревья игр и перебор — эталонные решения A1–D3."""
import random
from collections import deque
from functools import cache

# ---------- A. Перебор ----------

def subset_sums(nums: list[int], target: int) -> int:
    """A1. Сколько подмножеств (по позициям) имеют сумму target. Пустое — сумма 0."""
    def go(i, s):
        if i == len(nums):
            return int(s == target)
        return go(i + 1, s + nums[i]) + go(i + 1, s)
    return go(0, 0)


def n_queens(n: int) -> int:
    """A2. Число расстановок n ферзей на доске n×n без боя (перебор с возвратом)."""
    cols, d1, d2 = set(), set(), set()

    def go(r):
        if r == n:
            return 1
        total = 0
        for c in range(n):
            if c in cols or r + c in d1 or r - c in d2:
                continue
            cols.add(c), d1.add(r + c), d2.add(r - c)
            total += go(r + 1)
            cols.remove(c), d1.remove(r + c), d2.remove(r - c)
        return total
    return go(0)


def knight_distance(a: str, b: str) -> int:
    """A3. Наименьшее число ходов коня с клетки a на клетку b доски 8×8 ("a1".."h8"), поиск в ширину."""
    def xy(s):
        return ord(s[0]) - 97, int(s[1]) - 1
    start, goal = xy(a), xy(b)
    dist = {start: 0}
    q = deque([start])
    while q:
        x, y = q.popleft()
        if (x, y) == goal:
            return dist[x, y]
        for dx, dy in ((1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8 and (nx, ny) not in dist:
                dist[nx, ny] = dist[x, y] + 1
                q.append((nx, ny))
    raise AssertionError


def sliding_2x3(start: str) -> int:
    """A4*. Пятнашки 2×3: строка из 6 символов построчно, "_" — пустая клетка. Цель — "12345_".
    Ход — сдвинуть соседнюю (по стороне) фишку в пустую. Наименьшее число ходов или −1, если не собрать."""
    goal = "12345_"
    dist = {start: 0}
    q = deque([start])
    while q:
        s = q.popleft()
        if s == goal:
            return dist[s]
        i = s.index("_")
        r, c = divmod(i, 3)
        for dr, dc in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < 2 and 0 <= nc < 3:
                j = nr * 3 + nc
                t = list(s)
                t[i], t[j] = t[j], t[i]
                t = "".join(t)
                if t not in dist:
                    dist[t] = dist[s] + 1
                    q.append(t)
    return -1


# ---------- B. Деревья игр ----------

def nim(heaps: list[int]):
    """B1. Ним: ход — взять сколько угодно (≥ 1) камней из одной кучки, кто не может ходить — проиграл.
    Ответ — ("second", None), если ходящий проигрывает, иначе ("first", (номер кучки, сколько оставить)) —
    первый по номеру кучки выигрывающий ход."""
    x = 0
    for h in heaps:
        x ^= h
    if x == 0:
        return "second", None
    for i, h in enumerate(heaps):
        if h ^ x < h:
            return "first", (i, h ^ x)
    raise AssertionError


def game_value(tree, maximizing: bool = True) -> int:
    """B2. Дерево — вложенные списки, лист — число. В корне ходит максимизирующий, дальше по очереди."""
    if isinstance(tree, int):
        return tree
    vals = [game_value(t, not maximizing) for t in tree]
    return max(vals) if maximizing else min(vals)


def alphabeta_leaves(tree) -> list[int]:
    """B3. Какие листья посмотрит альфа-бета (слева направо, отсечение при alpha ≥ beta), по порядку."""
    seen = []

    def ab(t, alpha, beta, maximizing):
        if isinstance(t, int):
            seen.append(t)
            return t
        if maximizing:
            v = float("-inf")
            for ch in t:
                v = max(v, ab(ch, alpha, beta, False))
                alpha = max(alpha, v)
                if alpha >= beta:
                    break
        else:
            v = float("inf")
            for ch in t:
                v = min(v, ab(ch, alpha, beta, True))
                beta = min(beta, v)
                if alpha >= beta:
                    break
        return v

    ab(tree, float("-inf"), float("inf"), True)
    return seen


# ---------- C. Выигрышные позиции ----------

def ttt_games() -> dict[str, int]:
    """C1. Сколько разных партий крестиков-ноликов (последовательностей ходов до победы или заполнения):
    всего и по исходам. Ответ — {"total", "x", "o", "draw"}."""
    lines = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
    res = {"total": 0, "x": 0, "o": 0, "draw": 0}
    b = [0] * 9

    def go(p, filled):
        for i in range(9):
            if b[i]:
                continue
            b[i] = p
            if any(b[x] == b[y] == b[z] == p for x, y, z in lines if i in (x, y, z)):
                res["x" if p == 1 else "o"] += 1
                res["total"] += 1
            elif filled + 1 == 9:
                res["draw"] += 1
                res["total"] += 1
            else:
                go(-p, filled + 1)
            b[i] = 0
    go(1, 0)
    return res


def losing_positions(n: int, moves: set[int]) -> list[int]:
    """C2. Игра «бери камни»: можно взять k ∈ moves камней (если хватает), кто не может ходить — проиграл.
    Все проигрышные для ходящего позиции 0..n."""
    win = [False] * (n + 1)
    for s in range(n + 1):
        win[s] = any(k <= s and not win[s - k] for k in moves)
    return [s for s in range(n + 1) if not win[s]]


def grundy(n: int, moves: set[int]) -> list[int]:
    """C3. Числа Шпрага — Гранди позиций 0..n той же игры: g(s) = mex{g(s − k)}."""
    g = []
    for s in range(n + 1):
        reach = {g[s - k] for k in moves if k <= s}
        m = 0
        while m in reach:
            m += 1
        g.append(m)
    return g


def sum_winner(heaps: list[int], moves: set[int]) -> str:
    """C3. Несколько кучек, ход — в одной кучке по правилам C2. "first" или "second" — по XOR чисел Гранди."""
    g = grundy(max(heaps, default=0), moves)
    x = 0
    for h in heaps:
        x ^= g[h]
    return "first" if x else "second"


def principal_variation(tree, maximizing: bool = True) -> list[int]:
    """C4*. Главная линия: номера детей по пути от корня до листа при идеальной игре; при равенстве —
    левый ребёнок."""
    path = []
    while not isinstance(tree, int):
        vals = [game_value(t, not maximizing) for t in tree]
        best = max(vals) if maximizing else min(vals)
        i = vals.index(best)
        path.append(i)
        tree, maximizing = tree[i], not maximizing
    return path


# ---------- D. Ускорения ----------

def grid_paths(grid: list[str]) -> int:
    """D1. Сколько путей из левого верхнего угла в правый нижний ходами вправо и вниз, "#" — стена."""
    h, w = len(grid), len(grid[0])

    @cache
    def go(r, c):
        if r >= h or c >= w or grid[r][c] == "#":
            return 0
        if (r, c) == (h - 1, w - 1):
            return 1
        return go(r + 1, c) + go(r, c + 1)
    return go(0, 0)


def zobrist_table(cells: int, pieces: int, seed: int = 58) -> list[list[int]]:
    """D2. Таблица Зобриста: rng = random.Random(seed); table[клетка][фигура] = rng.getrandbits(64),
    перебор клеток снаружи, фигур внутри."""
    rng = random.Random(seed)
    return [[rng.getrandbits(64) for _ in range(pieces)] for _ in range(cells)]


def zobrist(board: list[int], table) -> int:
    """D2. Хэш доски: XOR table[i][v − 1] по всем клеткам с фигурой v ≥ 1 (0 — пусто)."""
    h = 0
    for i, v in enumerate(board):
        if v:
            h ^= table[i][v - 1]
    return h


def zobrist_move(h: int, cell: int, old: int, new: int, table) -> int:
    """D2. Хэш после замены фигуры в клетке cell с old на new за O(1)."""
    if old:
        h ^= table[cell][old - 1]
    if new:
        h ^= table[cell][new - 1]
    return h


def order_gain(tree) -> tuple[int, int]:
    """D3. Сколько листьев посмотрит альфа-бета (B3) в исходном порядке и после идеального упорядочения:
    у каждого узла дети отсортированы по их значению (B2) — лучшие для ходящего первыми, устойчиво."""
    def reorder(t, maximizing):
        if isinstance(t, int):
            return t
        kids = [reorder(ch, not maximizing) for ch in t]
        return sorted(kids, key=lambda ch: game_value(ch, not maximizing), reverse=maximizing)
    return len(alphabeta_leaves(tree)), len(alphabeta_leaves(reorder(tree, True)))
