"""Генератор нагрузки на asyncio (задача 7*)."""
import asyncio
import time


async def run_load(send, n_requests: int, concurrency: int) -> dict:
    """Выполнить n_requests вызовов await send(i) (i = 0..n−1), не больше concurrency одновременно.
    send возвращает HTTP-статус или бросает исключение (считаем статусом 0).
    Ответ: {"results": [(i, статус, мс)] по возрастанию i, "max_in_flight": наибольшее число
    одновременных вызовов, "elapsed_ms": общее время}. Мс — time.perf_counter, 1 знак."""
    if concurrency < 1:
        raise ValueError("concurrency >= 1")
    sem = asyncio.Semaphore(concurrency)
    in_flight = 0
    peak = 0
    results = []

    async def one(i):
        nonlocal in_flight, peak
        async with sem:
            in_flight += 1
            peak = max(peak, in_flight)
            t0 = time.perf_counter()
            try:
                status = await send(i)
            except Exception:  # noqa: BLE001 — любая ошибка клиента = неудачный запрос
                status = 0
            finally:
                in_flight -= 1
            results.append((i, status, round((time.perf_counter() - t0) * 1000, 1)))

    start = time.perf_counter()
    await asyncio.gather(*(one(i) for i in range(n_requests)))
    return {"results": sorted(results), "max_in_flight": peak,
            "elapsed_ms": round((time.perf_counter() - start) * 1000, 1)}
