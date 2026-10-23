"""Задача 2. Конечный автомат матча: lobby → countdown → playing → finished."""


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

    def _need(self, *states: str) -> None:
        if self.state not in states:
            raise InvalidTransition(f"нельзя в состоянии {self.state}")

    def join(self, name: str) -> None:
        self._need("lobby")
        if name in self.players:
            raise InvalidTransition("уже в матче")
        if len(self.players) >= self.max_players:
            raise InvalidTransition("матч заполнен")
        self.players.append(name)

    def set_ready(self, name: str) -> None:
        self._need("lobby")
        if name not in self.players:
            raise InvalidTransition("не в матче")
        self.ready.add(name)
        if len(self.players) >= self.min_players and self.ready == set(self.players):
            self.state, self.countdown = "countdown", self.countdown_ticks

    def leave(self, name: str) -> None:
        self._need("lobby", "countdown", "playing")
        if name not in self.players:
            raise InvalidTransition("не в матче")
        if self.state == "playing":
            self.died(name)
            return
        self.players.remove(name)
        self.ready.discard(name)
        if self.state == "countdown":
            self.state = "lobby"

    def tick(self) -> None:
        if self.state == "countdown":
            self.countdown -= 1
            if self.countdown == 0:
                self.state = "playing"
                self.alive = set(self.players)

    def died(self, name: str) -> None:
        self._need("playing")
        if name not in self.alive:
            return
        self.alive.discard(name)
        if len(self.alive) <= 1:
            self.state = "finished"
            self.winner = next(iter(self.alive), None)
