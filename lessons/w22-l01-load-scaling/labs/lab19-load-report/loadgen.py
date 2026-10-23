"""Генератор нагрузки на asyncio (задача 7*)."""
import asyncio  # noqa: F401
import time  # noqa: F401


async def run_load(send, n_requests: int, concurrency: int) -> dict:
    """Выполнить n_requests вызовов await send(i) (i = 0..n−1), не больше concurrency одновременно.
    send возвращает HTTP-статус или бросает исключение (считаем статусом 0).
    Ответ: {"results": [(i, статус, мс)] по возрастанию i, "max_in_flight": наибольшее число
    одновременных вызовов, "elapsed_ms": общее время}. Мс — time.perf_counter, 1 знак."""
    # TODO: asyncio.Semaphore, счётчик одновременных вызовов, gather
    raise NotImplementedError
