"""Эвристика и поиск с ограничением глубины для «Четырёх в ряд» (задача 5)."""
from search import INF, Stats

WIN = 1_000_000
WINDOW_SCORE = {2: 2, 3: 5}


def evaluate_c4(game, s) -> int:
    """Оценка позиции с точки зрения первого игрока. Для каждого «окна» из k клеток подряд (горизонталь,
    вертикаль, обе диагонали): если в окне фишки только одного игрока, j штук — WINDOW_SCORE.get(j, 0)
    этому игроку (плюс для 1, минус для −1). Плюс 3 за каждую фишку первого игрока в центральном столбце
    (cols // 2) и минус 3 за каждую фишку второго. Победа — ±WIN."""
    w = game.winner(s)
    if w in (1, -1):
        return w * WIN
    b, cols, rows, k = s[0], game.cols, game.rows, game.k
    score = 0
    for r in range(rows):
        for c in range(cols):
            for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
                er, ec = r + dr * (k - 1), c + dc * (k - 1)
                if not (0 <= er < rows and 0 <= ec < cols):
                    continue
                cells = [b[(r + dr * i) * cols + c + dc * i] for i in range(k)]
                a, o = cells.count(1), cells.count(-1)
                if a and not o:
                    score += WINDOW_SCORE.get(a, 0)
                elif o and not a:
                    score -= WINDOW_SCORE.get(o, 0)
    mid = cols // 2
    for r in range(rows):
        score += 3 * b[r * cols + mid]
    return score


def depth_limited(game, s, depth, evaluate, alpha=-INF, beta=INF, stats: Stats | None = None) -> int:
    """Альфа-бета с ограничением глубины. Победа на оставшейся глубине d — ±(WIN + d): быстрая победа
    лучше медленной, а поражение лучше оттянуть. Ничья — 0. depth = 0 — evaluate(game, s).
    Ходы перебираем от центра (search.center_first)."""
    from search import center_first

    if stats:
        stats.nodes += 1
    w = game.winner(s)
    if w is not None:
        return w * (WIN + depth) if w else 0
    if depth == 0:
        return evaluate(game, s)
    maximizing = game.to_move(s) == 1
    v = -INF if maximizing else INF
    for m in center_first(game, s, game.moves(s)):
        child = depth_limited(game, game.play(s, m), depth - 1, evaluate, alpha, beta, stats)
        if maximizing:
            v = max(v, child)
            alpha = max(alpha, v)
        else:
            v = min(v, child)
            beta = min(beta, v)
        if alpha >= beta:
            break
    return v


def choose_move(game, s, depth, evaluate=evaluate_c4):
    """Лучший ход по depth_limited (глубина хода — depth − 1 для потомков); при равенстве — первый
    в порядке center_first."""
    from search import center_first

    p = game.to_move(s)
    best, best_v = None, -INF
    for m in center_first(game, s, game.moves(s)):
        v = depth_limited(game, game.play(s, m), depth - 1, evaluate) * p
        if v > best_v:
            best, best_v = m, v
    return best
