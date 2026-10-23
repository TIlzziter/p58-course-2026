from collections import Counter

import pytest
from balancer import IpHash, LeastConn, RoundRobin


def test_round_robin_plain():
    rr = RoundRobin(["a", "b", "c"])
    assert [rr.pick() for _ in range(7)] == list("abcabca")


def test_smooth_weighted():
    rr = RoundRobin(["a", "b", "c"], [5, 1, 1])
    assert "".join(rr.pick() for _ in range(14)) == "aabacaa" * 2  # не «aaaaabc»: нагрузка размазана
    rr = RoundRobin(["x", "y"], [2, 1])
    assert "".join(rr.pick() for _ in range(6)) == "xyxxyx"


def test_weights_share():
    rr = RoundRobin(["a", "b", "c"], [3, 2, 1])
    c = Counter(rr.pick() for _ in range(600))
    assert c == {"a": 300, "b": 200, "c": 100}


def test_bad_weights():
    with pytest.raises(ValueError):
        RoundRobin(["a", "b"], [1])
    with pytest.raises(ValueError):
        RoundRobin(["a"], [0])


def test_least_conn():
    lc = LeastConn(["a", "b", "c"])
    assert [lc.pick() for _ in range(3)] == ["a", "b", "c"]
    lc.release("b")
    assert lc.pick() == "b"
    assert lc.pick() == "a"
    lc.release("c")
    lc.release("c")
    lc.release("c")
    assert lc.active["c"] == 0 and lc.pick() == "c"


def test_ip_hash():
    h = IpHash(["s1", "s2", "s3"])
    assert [h.pick(ip) for ip in ["10.0.0.1", "10.0.0.99", "10.0.1.5", "192.168.1.7", "8.8.8.8"]] == \
        ["s2", "s2", "s3", "s1", "s2"]
    assert h.pick("10.0.0.1") == h.pick("10.0.0.250")
    with pytest.raises(ValueError):
        h.pick(None)
