"""Логика «4 в ряд». Поле — список строк сверху вниз, 0 — пусто, 1 и 2 — игроки.

board[0] — верхняя строка, board[-1] — нижняя. Фишка падает на самую нижнюю свободную клетку столбца.
"""
from dataclasses import dataclass, field

ROWS, COLS = 6, 7
Board = list[list[int]]


class MoveError(ValueError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def new_board(rows: int = ROWS, cols: int = COLS) -> Board:
    return [[0] * cols] * rows


def drop(board: Board, col: int, player: int) -> int:
    """Бросить фишку в столбец col, вернуть номер строки, куда она упала."""
    for row in range(len(board)):
        if board[row][col] == 0:
            board[row][col] = player
            return row


def legal_moves(board: Board) -> list[int]:
    raise NotImplementedError("задача 3")


def winning_line(board: Board) -> list[tuple[int, int]]:
    """Клетки первой найденной четвёрки (по строкам сверху вниз, слева направо) или []."""
    rows, cols = len(board), len(board[0])
    for r in range(rows):
        for c in range(cols - 3):
            p = board[r][c]
            if p and all(board[r][c + i] == p for i in range(4)):
                return [(r, c + i) for i in range(4)]
    return []


def winner(board: Board) -> int:
    line = winning_line(board)
    return board[line[0][0]][line[0][1]] if line else 0


def status(board: Board) -> str:
    """"win1", "win2", "draw" или "playing"."""
    raise NotImplementedError("задача 5")


@dataclass
class Game:
    board: Board = field(default_factory=new_board)
    turn: int = 1
    moves: list[int] = field(default_factory=list)

    def play(self, col: int) -> str:
        drop(self.board, col, self.turn)
        self.moves.append(col)
        return status(self.board)

    def undo(self) -> None:
        raise NotImplementedError("задача 6")

    @classmethod
    def from_moves(cls, notation: str) -> "Game":
        """Партия из записи «4453...»: цифры — столбцы с 1 (как на доске для людей)."""
        raise NotImplementedError("задача 6")

    def to_json(self) -> dict:
        """Состояние для canvas-клиента."""
        raise NotImplementedError("задача 7")
