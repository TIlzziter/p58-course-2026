import asyncio

import pytest
from loadgen import run_load


def test_concurrency_limit_and_order():
    async def send(i):
        await asyncio.sleep(0.01)
        return 200

    res = asyncio.run(run_load(send, 40, 8))
    assert res["max_in_flight"] == 8
    assert [r[0] for r in res["results"]] == list(range(40))
    assert all(r[1] == 200 for r in res["results"])
    assert 45 <= res["elapsed_ms"] < 400  # 5 волн по 10 мс, а не 40 по 10
    assert all(r[2] >= 9 for r in res["results"])


def test_errors_are_status_zero():
    async def send(i):
        if i % 3 == 0:
            raise ConnectionError("нет связи")
        return 503 if i % 3 == 1 else 200

    res = asyncio.run(run_load(send, 9, 3))
    assert [r[1] for r in res["results"]] == [0, 503, 200] * 3


def test_serial():
    async def send(i):
        await asyncio.sleep(0.002)
        return 200

    res = asyncio.run(run_load(send, 5, 1))
    assert res["max_in_flight"] == 1


def test_bad_concurrency():
    async def send(i):
        return 200

    with pytest.raises(ValueError):
        asyncio.run(run_load(send, 1, 0))
