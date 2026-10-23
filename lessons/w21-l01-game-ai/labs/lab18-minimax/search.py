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
    # TODO: конец игры → winner; иначе max (ходит 1) или min (ходит -1) по детям
    raise NotImplementedError


def best_move(game, s, stats: Stats | None = None):
    """Задача 2. Лучший ход для того, кто ходит; при равенстве — первый в порядке moves()."""
    p = game.to_move(s)
    best, best_v = None, None
    for m in game.moves(s):
        v = minimax(game, game.play(s, m), stats)
        if best_v is None or v > best_v:  # BUG? а если ходит второй игрок
            best, best_v = m, v
    return best


def alphabeta(game, s, alpha=-INF, beta=INF, stats: Stats | None = None, order=None) -> int:
    """Задача 3. То же значение, что minimax, но с альфа-бета отсечением. order(game, s, moves) — порядок
    перебора (по умолчанию как в moves())."""
    if stats:
        stats.nodes += 1
    # TODO: как minimax, но с окном (alpha, beta): у максимизирующего alpha = max(alpha, v),
    # у минимизирующего beta = min(beta, v); alpha >= beta — дальше не перебираем
    raise NotImplementedError


def center_first(game, s, ms):
    """Задача 3. Порядок «от центра»: по |столбец − (cols − 1) / 2|, при равенстве — меньший номер."""
    return list(ms)  # TODO


def ab_best_move(game, s, stats: Stats | None = None, order=None):
    """Задача 3. Как best_move, но через alphabeta; окно сужается по уже найденному лучшему ходу."""
    raise NotImplementedError


def minimax_memo(game, s, cache: dict | None = None) -> int:
    """Задача 4. minimax с таблицей транспозиций: значение каждого состояния считаем один раз."""
    if cache is None:
        cache = {}
    w = game.winner(s)
    if w is not None:
        v = w
    else:
        vals = [minimax_memo(game, game.play(s, m), cache) for m in game.moves(s)]
        v = max(vals) if game.to_move(s) == 1 else min(vals)
    return v  # TODO: сохранить в cache
