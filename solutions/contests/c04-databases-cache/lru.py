"""E5*: LRU-кэш с ёмкостью и статистикой."""
from collections import OrderedDict


class LRU:
    def __init__(self, capacity: int):
        if capacity < 1:
            raise ValueError("capacity >= 1")
        self.capacity = capacity
        self.data: OrderedDict = OrderedDict()
        self.hits = self.misses = 0

    def get(self, key, default=None):
        if key in self.data:
            self.data.move_to_end(key)
            self.hits += 1
            return self.data[key]
        self.misses += 1
        return default

    def put(self, key, value) -> None:
        if key in self.data:
            self.data.move_to_end(key)
        self.data[key] = value
        if len(self.data) > self.capacity:
            self.data.popitem(last=False)

    def __len__(self) -> int:
        return len(self.data)

    def keys(self) -> list:
        """От самого старого использования к самому свежему."""
        return list(self.data)
