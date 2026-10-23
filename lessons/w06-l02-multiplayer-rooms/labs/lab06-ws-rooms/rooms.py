"""Комната на двух игроков. Комната ничего не знает о WebSocket:
каждый метод возвращает «исходящие» — список пар (кому, сообщение). Отправляет их app.py."""
from connect4 import Game, MoveError  # noqa: F401  (MoveError пригодится в handle)
from protocol import error  # noqa: F401

Out = list[tuple[str, dict]]


class RoomError(ValueError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


class Room:
    def __init__(self, room_id: str):
        self.id = room_id
        self.players: dict[str, int] = {}        # имя → цвет 1 или 2
        self.spectators: list[str] = []          # задача 7*
        self.game = Game()
        self.started = False
        self.finished = False

    def join(self, name: str, spectator: bool = False) -> Out:
        """Задача 2 (и 7* — зрители)."""
        color = len(self.players) + 1
        self.players[name] = color
        # TODO: name_taken, room_full; когда пришёл второй — всем {"type": "start", ...}
        return [(name, {"type": "welcome", "room": self.id, "color": color})]

    def everyone(self) -> list[str]:
        """Игроки по цвету, затем зрители — в этом порядке рассылаем."""
        return sorted(self.players, key=self.players.get) + self.spectators

    def broadcast(self, msg: dict) -> Out:
        return [(n, msg) for n in self.everyone()]

    def handle(self, name: str, msg: dict) -> Out:
        """Задачи 3–4: ход, чат, ping."""
        if msg["type"] == "ping":
            return self.broadcast({"type": "pong"})
        if msg["type"] == "chat":
            return [(name, {"type": "chat", "from": name, "text": msg["text"]})]
        raise NotImplementedError("задача 3: ход")

    def leave(self, name: str) -> Out:
        """Задача 5."""
        self.players.pop(name, None)
        return []

    @property
    def is_empty(self) -> bool:
        return not self.players and not self.spectators
