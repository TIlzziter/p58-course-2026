"""Контест 11 · E5*: решить «k в ряд» на маленьком поле с таблицей транспозиций."""
from functools import cache


def solve_connect(cols: int, rows: int, k: int) -> int:
    """Результат при идеальной игре: 1 — выигрывает первый, −1 — второй, 0 — ничья. Фишки падают вниз."""
    def win(board, idx, p):
        r, c = divmod(idx, cols)
        for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
            n = 1
            for sgn in (1, -1):
                rr, cc = r + dr * sgn, c + dc * sgn
                while 0 <= rr < rows and 0 <= cc < cols and board[rr * cols + cc] == p:
                    n += 1
                    rr, cc = rr + dr * sgn, cc + dc * sgn
            if n >= k:
                return True
        return False

    @cache
    def value(board, p):
        best = None
        any_move = False
        for c in range(cols):
            for r in range(rows):
                if board[r * cols + c] == 0:
                    break
            else:
                continue
            any_move = True
            i = r * cols + c
            b = board[:i] + (p,) + board[i + 1:]
            v = p if win(b, i, p) else value(b, -p)
            if v == p:
                return v
            if best is None or v * p > best * p:
                best = v
        return best if any_move else 0

    return value((0,) * (cols * rows), 1)
