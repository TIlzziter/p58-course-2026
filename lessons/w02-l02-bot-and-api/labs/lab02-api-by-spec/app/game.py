"""Логика крестиков-ноликов. Без FastAPI: чистые функции, легко тестировать."""

LINES = [(0, 1, 2), (3, 4, 5), (6, 7, 8)]   # TODO (задача 5): а столбцы и диагонали?


def winner(board: str) -> str | None:
    """Возвращает "X" или "O", если есть три в ряд, иначе None. board — 9 символов из "XO."."""
    for a, b, c in LINES:
        if board[a] == board[b] == board[c]:
            return board[a]
    return None


def is_draw(board: str) -> bool:
    """Ничья: свободных клеток нет и победителя нет."""
    raise NotImplementedError("задача 5")


def place(board: str, cell: int, mark: str) -> str:
    """Новая доска с меткой mark в клетке cell. Клетка должна быть свободна, иначе ValueError."""
    return board[:cell] + mark + board[cell + 1:]
