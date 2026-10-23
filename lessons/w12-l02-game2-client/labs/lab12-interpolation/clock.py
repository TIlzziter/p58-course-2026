"""Задача 4. Синхронизация часов клиента с сервером.

Замер: клиент отправил ping в sent (свои часы), сервер ответил своим временем server, ответ пришёл в received.
"""


class ClockSync:
    def __init__(self, keep: int = 8):
        self.keep = keep
        self.samples: list[tuple[float, float, float]] = []

    def add(self, sent: float, server: float, received: float) -> None:
        self.samples.append((sent, server, received))

    @property
    def offset(self) -> float:
        """Смещение «сервер − клиент» по замеру с наименьшим RTT среди последних keep (при равенстве — свежий)."""
        sent, server, received = self.samples[-1]
        return server - received

    @property
    def rtt(self) -> float:
        sent, _, received = self.samples[-1]
        return received - sent

    def server_now(self, client_now: float) -> float:
        return client_now + self.offset
