"""Комната лобби: вход, выход, хост, готовность."""


class RoomFull(Exception):
    pass


class NotInRoom(Exception):
    pass


class Room:
    def __init__(self, code: str, capacity: int = 4):
        self.code = code
        self.capacity = capacity
        self.players: list[str] = []       # в порядке входа
        self.ready: set[str] = set()

    @property
    def host(self) -> str | None:
        """Хост — тот, кто дольше всех в комнате. Пустая комната — None."""
        return self.players[0] if self.players else None

    def join(self, user: str) -> bool:
        """Войти. Уже в комнате — ничего не меняем, False. Полная — RoomFull."""
        if user in self.players:
            return False
        if len(self.players) >= self.capacity:
            raise RoomFull(self.code)
        self.players.append(user)
        return True

    def leave(self, user: str) -> None:
        """Выйти. Нет в комнате — NotInRoom. Отметка «готов» снимается."""
        if user not in self.players:
            raise NotInRoom(user)
        self.players.remove(user)
        self.ready.discard(user)

    def set_ready(self, user: str, value: bool = True) -> None:
        if user not in self.players:
            raise NotInRoom(user)
        if value:
            self.ready.add(user)
        else:
            self.ready.discard(user)

    def can_start(self) -> bool:
        """Старт: хотя бы двое и все готовы."""
        return len(self.players) >= 2 and all(p in self.ready for p in self.players)
