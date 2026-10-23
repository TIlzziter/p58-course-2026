"""Комната на двух игроков (эталон). Комната ничего не знает о WebSocket:
каждый метод возвращает «исходящие» — список пар (кому, сообщение)."""
from connect4 import Game, MoveError
from protocol import error

Out = list[tuple[str, dict]]


class RoomError(ValueError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


class Room:
    def __init__(self, room_id: str):
        self.id = room_id
        self.players: dict[str, int] = {}        # имя → цвет 1 или 2
        self.spectators: list[str] = []
        self.game = Game()
        self.started = False
        self.finished = False

    # ---------- задача 2 ----------
    def join(self, name: str, spectator: bool = False) -> Out:
        if name in self.players or name in self.spectators:
            raise RoomError("name_taken")
        if spectator:                                         # задача 7*
            self.spectators.append(name)
            return [(name, {"type": "welcome", "room": self.id, "color": 0, "state": self.game.to_json()})]
        if len(self.players) == 2 or self.started:
            raise RoomError("room_full")
        color = 1 if 1 not in self.players.values() else 2
        self.players[name] = color
        out: Out = [(name, {"type": "welcome", "room": self.id, "color": color})]
        if len(self.players) == 2:
            self.started = True
            names = {str(c): n for n, c in self.players.items()}
            out += self.broadcast({"type": "start", "players": names, "state": self.game.to_json()})
        return out

    def everyone(self) -> list[str]:
        return sorted(self.players, key=self.players.get) + self.spectators

    def broadcast(self, msg: dict) -> Out:
        return [(n, msg) for n in self.everyone()]

    # ---------- задачи 3–4 ----------
    def handle(self, name: str, msg: dict) -> Out:
        if msg["type"] == "ping":
            return [(name, {"type": "pong"})]
        if msg["type"] == "chat":
            return self.broadcast({"type": "chat", "from": name, "text": msg["text"]})
        if name not in self.players:
            return [(name, error("spectator"))]
        if not self.started:
            return [(name, error("not_started"))]
        if self.finished:
            return [(name, error("game_over"))]
        color = self.players[name]
        if color != self.game.turn:
            return [(name, error("not_your_turn"))]
        try:
            result = self.game.play(msg["col"])
        except MoveError as e:
            return [(name, error(e.code))]
        out = self.broadcast({"type": "state", "state": self.game.to_json(), "last": {"col": msg["col"], "by": color}})
        if result != "playing":
            self.finished = True
            out += self.broadcast({"type": "game_over", "result": result})
        return out

    # ---------- задача 5 ----------
    def leave(self, name: str) -> Out:
        if name in self.spectators:
            self.spectators.remove(name)
            return []
        if name not in self.players:
            return []
        color = self.players.pop(name)
        out = self.broadcast({"type": "opponent_left", "name": name})
        if self.started and not self.finished:
            self.finished = True
            out += self.broadcast({"type": "game_over", "result": f"win{3 - color}", "reason": "forfeit"})
        return out

    @property
    def is_empty(self) -> bool:
        return not self.players and not self.spectators
