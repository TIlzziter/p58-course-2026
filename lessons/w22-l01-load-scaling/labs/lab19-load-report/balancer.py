"""Балансировщики как в Nginx upstream (задача 5)."""
import zlib


class RoundRobin:
    """Плавный взвешенный round-robin Nginx: при каждом выборе current[i] += weight[i]; берём сервер
    с наибольшим current (при равенстве — первый), ему current -= сумма весов."""

    def __init__(self, servers: list[str], weights: list[int] | None = None):
        self.servers = list(servers)
        self.weights = list(weights) if weights else [1] * len(servers)
        self.current = [0] * len(servers)

    def pick(self, client: str | None = None) -> str:
        # TODO: плавный взвешенный алгоритм; сейчас — простой по кругу без весов
        i = sum(self.current) % len(self.servers)
        self.current[0] += 1
        return self.servers[i]


class LeastConn:
    """least_conn: сервер с наименьшим числом активных запросов (при равенстве — первый).
    pick увеличивает счётчик, release(server) — уменьшает (не ниже 0)."""

    def __init__(self, servers: list[str]):
        self.servers = list(servers)
        self.active = dict.fromkeys(self.servers, 0)

    def pick(self, client: str | None = None) -> str:
        raise NotImplementedError

    def release(self, server: str) -> None:
        raise NotImplementedError


class IpHash:
    """ip_hash: клиенты из одной сети /24 всегда на одном сервере: zlib.crc32(первые три октета через точку)
    % число серверов."""

    def __init__(self, servers: list[str]):
        self.servers = list(servers)

    def pick(self, client: str | None = None) -> str:
        return self.servers[zlib.crc32(client.encode()) % len(self.servers)]  # TODO: сеть /24, None
