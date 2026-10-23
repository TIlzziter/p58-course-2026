"""Игры для ИИ-соперника. Общий интерфейс:

    initial()        — начальное состояние (неизменяемое, можно класть в dict)
    to_move(s)       — кто ходит: 1 (первый игрок) или -1
    moves(s)         — список ходов в фиксированном порядке
    play(s, m)       — новое состояние после хода m (старое не меняется)
    winner(s)        — 1 или -1, если кто-то выиграл; 0 — ничья; None — игра идёт

Состояние — пара (board, to_move), board — кортеж клеток 0 / 1 / -1.
"""

LINES_3 = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]


class TicTacToe:
    """Крестики-нолики 3×3, клетки 0..8 построчно."""

    def initial(self):
        return (0,) * 9, 1

    def to_move(self, s):
        return s[1]

    def moves(self, s):
        if self.winner(s) is not None:
            return []
        return [i for i, v in enumerate(s[0]) if v == 0]

    def play(self, s, m):
        board, p = s
        if board[m] != 0:
            raise ValueError(f"клетка {m} занята")
        b = list(board)
        b[m] = p
        return tuple(b), -p

    def winner(self, s):
        b = s[0]
        for x, y, z in LINES_3:
            if b[x] != 0 and b[x] == b[y] == b[z]:
                return b[x]
        return 0 if all(b) else None

    @staticmethod
    def parse(text: str):
        """'X.O/.X./...' → состояние; ходит тот, у кого меньше фишек (при равенстве — X)."""
        cells = [{"X": 1, "O": -1, ".": 0}[c] for c in text.replace("/", "")]
        p = 1 if cells.count(1) == cells.count(-1) else -1
        return tuple(cells), p


class ConnectFour:
    """«Четыре в ряд» на поле cols × rows, нужно k в ряд. Клетка (r, c) — индекс r*cols + c, r = 0 — низ.
    Ход — номер столбца; фишка падает на самую нижнюю свободную клетку."""

    def __init__(self, cols: int = 7, rows: int = 6, k: int = 4):
        self.cols, self.rows, self.k = cols, rows, k

    def initial(self):
        return (0,) * (self.cols * self.rows), 1

    def to_move(self, s):
        return s[1]

    def moves(self, s):
        if self.winner(s) is not None:
            return []
        top = (self.rows - 1) * self.cols
        return [c for c in range(self.cols) if s[0][top + c] == 0]

    def play(self, s, col):
        board, p = s
        for r in range(self.rows):
            i = r * self.cols + col
            if board[i] == 0:
                b = list(board)
                b[i] = p
                return tuple(b), -p
        raise ValueError(f"столбец {col} заполнен")

    def winner(self, s):
        """Задача 1: k одинаковых фишек подряд по горизонтали, вертикали или диагонали → 1 или -1;
        поле заполнено без победы → 0; иначе None."""
        b, cols, rows, k = s[0], self.cols, self.rows, self.k
        for r in range(rows):
            for c in range(cols):
                v = b[r * cols + c]
                if v == 0:
                    continue
                for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
                    er, ec = r + dr * (k - 1), c + dc * (k - 1)
                    if not (0 <= er < rows and 0 <= ec < cols):
                        continue
                    if all(b[(r + dr * i) * cols + c + dc * i] == v for i in range(1, k)):
                        return v
        return 0 if all(b) else None

    def parse(self, text: str):
        """Строки сверху вниз через '/', 'X' 'O' '.'; ходит тот, у кого меньше фишек."""
        rows = text.split("/")[::-1]
        cells = [{"X": 1, "O": -1, ".": 0}[ch] for row in rows for ch in row]
        p = 1 if cells.count(1) == cells.count(-1) else -1
        return tuple(cells), p
