"""Логика «4 в ряд» из лабораторной 04 (готовая, менять не нужно). Поле — список строк сверху вниз, 0 — пусто, 1 и 2 — игроки."""
from dataclasses import dataclass, field

ROWS, COLS = 6, 7
Board = list[list[int]]
DIRECTIONS = [(0, 1), (1, 0), (1, 1), (1, -1)]


class MoveError(ValueError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def new_board(rows: int = ROWS, cols: int = COLS) -> Board:
    if rows < 4 or cols < 4:
        raise ValueError("поле должно быть не меньше 4×4")
    return [[0] * cols for _ in range(rows)]


def drop(board: Board, col: int, player: int) -> int:
    """Бросить фишку в столбец col, вернуть номер строки, куда она упала."""
    if player not in (1, 2):
        raise ValueError("игрок — 1 или 2")
    if not 0 <= col < len(board[0]):
        raise MoveError("bad_column")
    for row in range(len(board) - 1, -1, -1):
        if board[row][col] == 0:
            board[row][col] = player
            return row
    raise MoveError("column_full")


def legal_moves(board: Board) -> list[int]:
    return [c for c in range(len(board[0])) if board[0][c] == 0]


def winning_line(board: Board) -> list[tuple[int, int]]:
    """Клетки первой найденной четвёрки (по строкам сверху вниз, слева направо) или []."""
    rows, cols = len(board), len(board[0])
    for r in range(rows):
        for c in range(cols):
            p = board[r][c]
            if p == 0:
                continue
            for dr, dc in DIRECTIONS:
                cells = [(r + i * dr, c + i * dc) for i in range(4)]
                if all(0 <= rr < rows and 0 <= cc < cols and board[rr][cc] == p for rr, cc in cells):
                    return cells
    return []


def winner(board: Board) -> int:
    line = winning_line(board)
    return board[line[0][0]][line[0][1]] if line else 0


def status(board: Board) -> str:
    """"win1", "win2", "draw" или "playing"."""
    w = winner(board)
    if w:
        return f"win{w}"
    return "draw" if not legal_moves(board) else "playing"


@dataclass
class Game:
    board: Board = field(default_factory=new_board)
    turn: int = 1
    moves: list[int] = field(default_factory=list)

    def play(self, col: int) -> str:
        if status(self.board) != "playing":
            raise MoveError("game_over")
        drop(self.board, col, self.turn)
        self.moves.append(col)
        self.turn = 3 - self.turn
        return status(self.board)

    def undo(self) -> None:
        if not self.moves:
            raise MoveError("nothing_to_undo")
        col = self.moves.pop()
        for row in range(len(self.board)):
            if self.board[row][col]:
                self.board[row][col] = 0
                break
        self.turn = 3 - self.turn

    @classmethod
    def from_moves(cls, notation: str) -> "Game":
        """Партия из записи «4453...»: цифры — столбцы с 1 (как на доске для людей)."""
        g = cls()
        for ch in notation.strip():
            if not ch.isdigit() or ch == "0":
                raise MoveError("bad_notation")
            g.play(int(ch) - 1)
        return g

    def to_json(self) -> dict:
        """Состояние для canvas-клиента."""
        return {"board": [row[:] for row in self.board], "turn": self.turn, "status": status(self.board),
                "win_cells": [list(c) for c in winning_line(self.board)], "moves": len(self.moves)}
