"""Перебор дерева игры. Все значения — с точки зрения первого игрока: +1 выигрывает первый, −1 — второй,
0 — ничья. Первый игрок (to_move = 1) максимизирует, второй — минимизирует."""
from dataclasses import dataclass

INF = float("inf")


@dataclass
class Stats:
    nodes: int = 0  # сколько раз функция поиска вызвана на каком-то состоянии


def minimax(game, s, stats: Stats | None = None) -> int:
    """Задача 2. Значение позиции при идеальной игре обоих."""
    if stats:
        stats.nodes += 1
    w = game.winner(s)
    if w is not None:
        return w
    vals = [minimax(game, game.play(s, m), stats) for m in game.moves(s)]
    return max(vals) if game.to_move(s) == 1 else min(vals)


def best_move(game, s, stats: Stats | None = None):
    """Задача 2. Лучший ход для того, кто ходит; при равенстве — первый в порядке moves()."""
    p = game.to_move(s)
    best, best_v = None, None
    for m in game.moves(s):
        v = minimax(game, game.play(s, m), stats)
        if best_v is None or v * p > best_v * p:
            best, best_v = m, v
    return best


def alphabeta(game, s, alpha=-INF, beta=INF, stats: Stats | None = None, order=None) -> int:
    """Задача 3. То же значение, что minimax, но с альфа-бета отсечением. order(game, s, moves) — порядок
    перебора (по умолчанию как в moves())."""
    if stats:
        stats.nodes += 1
    w = game.winner(s)
    if w is not None:
        return w
    ms = game.moves(s)
    if order:
        ms = order(game, s, ms)
    if game.to_move(s) == 1:
        v = -INF
        for m in ms:
            v = max(v, alphabeta(game, game.play(s, m), alpha, beta, stats, order))
            alpha = max(alpha, v)
            if alpha >= beta:
                break
    else:
        v = INF
        for m in ms:
            v = min(v, alphabeta(game, game.play(s, m), alpha, beta, stats, order))
            beta = min(beta, v)
            if alpha >= beta:
                break
    return v


def center_first(game, s, ms):
    """Задача 3. Порядок «от центра»: по |столбец − (cols − 1) / 2|, при равенстве — меньший номер."""
    mid = (game.cols - 1) / 2
    return sorted(ms, key=lambda c: (abs(c - mid), c))


def ab_best_move(game, s, stats: Stats | None = None, order=None):
    """Задача 3. Как best_move, но через alphabeta; окно сужается по уже найденному лучшему ходу."""
    p = game.to_move(s)
    ms = order(game, s, game.moves(s)) if order else game.moves(s)
    best, best_v = None, -INF
    alpha, beta = -INF, INF
    for m in ms:
        v = alphabeta(game, game.play(s, m), alpha, beta, stats, order)
        if best is None or v * p > best_v:
            best, best_v = m, v * p
        if p == 1:
            alpha = max(alpha, v)
        else:
            beta = min(beta, v)
    return best


def minimax_memo(game, s, cache: dict | None = None) -> int:
    """Задача 4. minimax с таблицей транспозиций: значение каждого состояния считаем один раз."""
    if cache is None:
        cache = {}
    if s in cache:
        return cache[s]
    w = game.winner(s)
    if w is not None:
        v = w
    else:
        vals = [minimax_memo(game, game.play(s, m), cache) for m in game.moves(s)]
        v = max(vals) if game.to_move(s) == 1 else min(vals)
    cache[s] = v
    return v
