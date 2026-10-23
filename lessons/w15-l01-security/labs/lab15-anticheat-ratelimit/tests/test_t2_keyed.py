import pytest
from ratelimit import KeyedLimiter


def test_limit_per_key(clock):
    lim = KeyedLimiter(limit=3, window=10, now=clock)
    assert [lim.hit("ann")[0] for _ in range(4)] == [True, True, True, False]
    assert lim.hit("bob") == (True, 0.0)            # у другого ключа своё окно


def test_sliding_window(clock):
    lim = KeyedLimiter(limit=2, window=10, now=clock)
    lim.hit("a")                                      # t = 1000
    clock.tick(4)
    lim.hit("a")                                      # t = 1004
    clock.tick(2)
    ok, retry = lim.hit("a")                          # t = 1006: окно (996, 1006] полное
    assert not ok and retry == pytest.approx(4)
    clock.tick(4)                                     # t = 1010: событие 1000 уже не в окне (1000, 1010]
    assert lim.hit("a") == (True, 0.0)
    ok, retry = lim.hit("a")
    assert not ok and retry == pytest.approx(4)       # старейшее теперь 1004


def test_rejected_do_not_count(clock):
    lim = KeyedLimiter(limit=1, window=10, now=clock)
    lim.hit("a")
    for _ in range(5):
        clock.tick(1)
        assert not lim.hit("a")[0]                    # спамим отказами
    clock.tick(5)                                     # прошло 10 с от единственного разрешённого
    assert lim.hit("a")[0]


def test_cleanup(clock):
    lim = KeyedLimiter(limit=2, window=10, now=clock)
    for k in ("a", "b", "c"):
        lim.hit(k)
    clock.tick(5)
    lim.hit("c")
    assert len(lim) == 3
    clock.tick(6)
    lim.cleanup()
    assert len(lim) == 1                              # у «c» событие 1005 ещё в окне
    clock.tick(10)
    lim.cleanup()
    assert len(lim) == 0
