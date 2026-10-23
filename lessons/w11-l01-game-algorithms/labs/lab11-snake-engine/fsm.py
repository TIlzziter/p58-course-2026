"""Задача 2. Конечный автомат матча: lobby → countdown → playing → finished.

Таблица переходов — в README. Недопустимое действие → InvalidTransition.
"""


class InvalidTransition(ValueError):
    pass


class Match:
    def __init__(self, min_players: int = 2, max_players: int = 4, countdown: int = 3):
        self.min_players, self.max_players, self.countdown_ticks = min_players, max_players, countdown
        self.state = "lobby"
        self.players: list[str] = []
        self.ready: set[str] = set()
        self.alive: set[str] = set()
        self.countdown = 0
        self.winner: str | None = None

    def join(self, name: str) -> None:
        self.players.append(name)

    def set_ready(self, name: str) -> None:
        self.ready.add(name)
        if self.ready == set(self.players):
            self.state, self.countdown = "countdown", self.countdown_ticks

    def leave(self, name: str) -> None:
        raise NotImplementedError

    def tick(self) -> None:
        if self.state == "countdown":
            self.countdown -= 1
            if self.countdown == 0:
                self.state = "playing"

    def died(self, name: str) -> None:
        raise NotImplementedError
