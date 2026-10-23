"""Контест 3, E4 · босс и E5* — «Морской бой» (эталон)."""
SIZE = 10


class ShotError(ValueError):
    pass


def ship_cells(r: int, c: int, length: int, horizontal: bool) -> list[tuple[int, int]]:
    return [(r, c + i) if horizontal else (r + i, c) for i in range(length)]


class Fleet:
    """а) Расстановка: корабли не выходят за поле 10×10 и не касаются даже углами."""

    def __init__(self):
        self.ships: list[set[tuple[int, int]]] = []
        self.hits: set[tuple[int, int]] = set()
        self.shots: set[tuple[int, int]] = set()

    def place(self, r: int, c: int, length: int, horizontal: bool) -> None:
        cells = ship_cells(r, c, length, horizontal)
        if not all(0 <= rr < SIZE and 0 <= cc < SIZE for rr, cc in cells):
            raise ValueError("за границей поля")
        taken = set().union(*self.ships) if self.ships else set()
        for rr, cc in cells:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if (rr + dr, cc + dc) in taken:
                        raise ValueError("касается другого корабля")
        self.ships.append(set(cells))

    # б)
    def shoot(self, r: int, c: int) -> str:
        if not (0 <= r < SIZE and 0 <= c < SIZE):
            raise ShotError("за границей поля")
        if (r, c) in self.shots:
            raise ShotError("сюда уже стреляли")
        self.shots.add((r, c))
        for ship in self.ships:
            if (r, c) in ship:
                self.hits.add((r, c))
                return "sunk" if ship <= self.hits else "hit"
        return "miss"

    def all_sunk(self) -> bool:
        return all(ship <= self.hits for ship in self.ships)

    def view(self) -> list[str]:
        """Что видит соперник: . — не стреляли, o — мимо, x — ранен, # — потоплен."""
        sunk = set().union(*(s for s in self.ships if s <= self.hits)) if self.ships else set()
        rows = []
        for r in range(SIZE):
            line = ""
            for c in range(SIZE):
                if (r, c) in sunk:
                    line += "#"
                elif (r, c) in self.hits:
                    line += "x"
                elif (r, c) in self.shots:
                    line += "o"
                else:
                    line += "."
            rows.append(line)
        return rows


class Battle:
    """в) Два игрока; после попадания стреляет тот же, после промаха — ход переходит."""

    def __init__(self, fleet_a: Fleet, fleet_b: Fleet):
        self.fleets = [fleet_a, fleet_b]
        self.turn = 0
        self.winner: int | None = None

    def fire(self, player: int, r: int, c: int) -> str:
        if self.winner is not None:
            raise ShotError("игра окончена")
        if player != self.turn:
            raise ShotError("не ваш ход")
        result = self.fleets[1 - player].shoot(r, c)
        if self.fleets[1 - player].all_sunk():
            self.winner = player
            return "win"
        if result == "miss":
            self.turn = 1 - self.turn
        return result


def next_shot(view: list[str]) -> tuple[int, int]:
    """E5*. Добивание: если есть ранение (x) — первая по порядку свободная клетка рядом с ним
    (если ранений в линию два и больше — только по этой линии); иначе первая свободная клетка «шахматки» (r + c) % 2 == 0,
    иначе любая первая свободная."""
    n = len(view)
    free = lambda r, c: 0 <= r < n and 0 <= c < n and view[r][c] == "."
    hits = [(r, c) for r in range(n) for c in range(n) if view[r][c] == "x"]
    if hits:
        rows = {r for r, _ in hits}
        cols = {c for _, c in hits}
        if len(hits) >= 2 and len(rows) == 1:
            r = hits[0][0]
            cands = [(r, min(cols) - 1), (r, max(cols) + 1)]
        elif len(hits) >= 2 and len(cols) == 1:
            c = hits[0][1]
            cands = [(min(rows) - 1, c), (max(rows) + 1, c)]
        else:
            r, c = hits[0]
            cands = [(r - 1, c), (r, c + 1), (r + 1, c), (r, c - 1)]
        for cell in cands:
            if free(*cell):
                return cell
    for parity in (True, False):
        for r in range(n):
            for c in range(n):
                if free(r, c) and (((r + c) % 2 == 0) or not parity):
                    return r, c
    raise ValueError("нет свободных клеток")
