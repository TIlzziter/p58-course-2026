"""Подбор соперников: ждём, пока наберётся группа."""
import asyncio


class Matchmaker:
    def __init__(self, size: int = 2, timeout: float = 10.0):
        self.size = size
        self.timeout = timeout
        self.queue: list[tuple[str, asyncio.Future]] = []

    def waiting(self) -> list[str]:
        return [u for u, _ in self.queue]

    async def find(self, user: str) -> list[str]:
        """Встать в очередь и дождаться группы из size игроков (в порядке очереди).

        Уже в очереди — ValueError. Не дождались за timeout секунд — уходим из очереди, TimeoutError.
        """
        if user in self.waiting():
            raise ValueError(f"{user} уже в очереди")
        fut = asyncio.get_running_loop().create_future()
        self.queue.append((user, fut))
        if len(self.queue) >= self.size:
            group, self.queue = self.queue[: self.size], self.queue[self.size :]
            names = [u for u, _ in group]
            for _, f in group:
                f.set_result(names)
        try:
            return await asyncio.wait_for(fut, self.timeout)
        except TimeoutError:
            self.cancel(user)
            raise

    def cancel(self, user: str) -> bool:
        """Убрать из очереди; True, если был."""
        before = len(self.queue)
        self.queue = [(u, f) for u, f in self.queue if u != user]
        return len(self.queue) < before
