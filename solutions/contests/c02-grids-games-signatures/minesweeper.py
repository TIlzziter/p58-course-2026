"""Контест 2, E4 · босс — «Сапёр» (эталон)."""
from collections import deque


class GameOver(Exception):
    pass


class Minesweeper:
    def __init__(self, rows: int, cols: int, mines: set[tuple[int, int]]):
        self.rows, self.cols = rows, cols
        self.mines = set(mines)
        self.opened: set[tuple[int, int]] = set()
        self.flags: set[tuple[int, int]] = set()
        self.status = "playing"

    def neighbors(self, r: int, c: int):
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if (dr or dc) and 0 <= r + dr < self.rows and 0 <= c + dc < self.cols:
                    yield r + dr, c + dc

    # а)
    def count(self, r: int, c: int) -> int:
        return sum((n in self.mines) for n in self.neighbors(r, c))

    def view(self) -> list[str]:
        out = []
        for r in range(self.rows):
            line = ""
            for c in range(self.cols):
                if self.status == "lost" and (r, c) in self.mines:
                    line += "*"
                elif (r, c) in self.opened:
                    k = self.count(r, c)
                    line += str(k) if k else "."
                elif (r, c) in self.flags:
                    line += "F"
                else:
                    line += "#"
            out.append(line)
        return out

    # б)
    def open(self, r: int, c: int) -> int:
        if self.status != "playing":
            raise GameOver(self.status)
        if (r, c) in self.opened or (r, c) in self.flags:
            return 0
        if (r, c) in self.mines:
            self.status = "lost"
            return 0
        opened = 0
        queue = deque([(r, c)])
        self.opened.add((r, c))
        while queue:
            cell = queue.popleft()
            opened += 1
            if self.count(*cell) == 0:
                for n in self.neighbors(*cell):
                    if n not in self.opened and n not in self.flags and n not in self.mines:
                        self.opened.add(n)
                        queue.append(n)
        if len(self.opened) == self.rows * self.cols - len(self.mines):
            self.status = "won"
        return opened

    # в)
    def flag(self, r: int, c: int) -> bool:
        """Поставить/снять флаг на закрытой клетке. Возвращает, стоит ли флаг после вызова."""
        if self.status != "playing":
            raise GameOver(self.status)
        if (r, c) in self.opened:
            return False
        if (r, c) in self.flags:
            self.flags.remove((r, c))
            return False
        self.flags.add((r, c))
        return True

    def mines_left(self) -> int:
        return len(self.mines) - len(self.flags)
