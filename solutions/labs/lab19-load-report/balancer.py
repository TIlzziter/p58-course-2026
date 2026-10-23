"""Балансировщики как в Nginx upstream (задача 5)."""
import zlib


class RoundRobin:
    """Плавный взвешенный round-robin Nginx: при каждом выборе current[i] += weight[i]; берём сервер
    с наибольшим current (при равенстве — первый), ему current -= сумма весов."""

    def __init__(self, servers: list[str], weights: list[int] | None = None):
        self.servers = list(servers)
        self.weights = list(weights) if weights else [1] * len(servers)
        if len(self.weights) != len(self.servers) or min(self.weights) <= 0:
            raise ValueError("веса")
        self.current = [0] * len(servers)

    def pick(self, client: str | None = None) -> str:
        total = sum(self.weights)
        for i, w in enumerate(self.weights):
            self.current[i] += w
        best = max(range(len(self.servers)), key=lambda i: (self.current[i], -i))
        self.current[best] -= total
        return self.servers[best]


class LeastConn:
    """least_conn: сервер с наименьшим числом активных запросов (при равенстве — первый).
    pick увеличивает счётчик, release(server) — уменьшает (не ниже 0)."""

    def __init__(self, servers: list[str]):
        self.servers = list(servers)
        self.active = dict.fromkeys(self.servers, 0)

    def pick(self, client: str | None = None) -> str:
        s = min(self.servers, key=lambda x: self.active[x])
        self.active[s] += 1
        return s

    def release(self, server: str) -> None:
        self.active[server] = max(0, self.active[server] - 1)


class IpHash:
    """ip_hash: клиенты из одной сети /24 всегда на одном сервере: zlib.crc32(первые три октета через точку)
    % число серверов."""

    def __init__(self, servers: list[str]):
        self.servers = list(servers)

    def pick(self, client: str | None = None) -> str:
        if client is None:
            raise ValueError("нужен IP клиента")
        key = ".".join(client.split(".")[:3]).encode()
        return self.servers[zlib.crc32(key) % len(self.servers)]
