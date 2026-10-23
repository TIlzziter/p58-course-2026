import pytest
from ratelimit import TokenBucket


def test_starts_full_then_empty(clock):
    b = TokenBucket(rate=2, capacity=3, now=clock)
    assert [b.allow() for _ in range(4)] == [True, True, True, False]


def test_refill_rate(clock):
    b = TokenBucket(rate=2, capacity=3, now=clock)
    for _ in range(3):
        b.allow()
    clock.tick(0.4)                       # 0.8 токена — мало
    assert not b.allow()
    clock.tick(0.1)                       # ровно 1.0
    assert b.allow()
    assert not b.allow()


def test_capacity_cap(clock):
    b = TokenBucket(rate=2, capacity=3, now=clock)
    clock.tick(100)                       # за долгий простой не копим больше 3
    assert [b.allow() for _ in range(4)] == [True, True, True, False]


def test_cost_and_retry_after(clock):
    b = TokenBucket(rate=2, capacity=3, now=clock)
    assert b.retry_after() == 0.0
    assert b.allow(cost=2)
    assert not b.allow(cost=2)            # отказ ничего не списывает
    assert b.retry_after(cost=2) == pytest.approx(0.5)
    assert b.allow(cost=1)
    assert b.retry_after(cost=3) == pytest.approx(1.5)
    with pytest.raises(ValueError):
        b.allow(cost=4)
    with pytest.raises(ValueError):
        b.retry_after(cost=4)
