"""Логика крестиков-ноликов. Без FastAPI: чистые функции, легко тестировать."""

LINES = [(0, 1, 2), (3, 4, 5), (6, 7, 8),
         (0, 3, 6), (1, 4, 7), (2, 5, 8),
         (0, 4, 8), (2, 4, 6)]


def winner(board: str) -> str | None:
    """Возвращает "X" или "O", если есть три в ряд, иначе None. board — 9 символов из "XO."."""
    for a, b, c in LINES:
        if board[a] != "." and board[a] == board[b] == board[c]:
            return board[a]
    return None


def is_draw(board: str) -> bool:
    return "." not in board and winner(board) is None


def place(board: str, cell: int, mark: str) -> str:
    """Новая доска с меткой mark в клетке cell. Клетка должна быть свободна."""
    if board[cell] != ".":
        raise ValueError("cell_taken")
    return board[:cell] + mark + board[cell + 1:]
