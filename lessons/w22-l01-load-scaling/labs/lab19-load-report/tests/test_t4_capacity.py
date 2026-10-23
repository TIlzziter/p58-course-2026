import pytest
from capacity import concurrency, max_rps, replicas_needed, utilization


def test_little():
    assert concurrency(200, 150) == 30.0
    assert concurrency(100, 25) == 2.5
    assert concurrency(0, 100) == 0


def test_max_rps():
    assert max_rps(4, 50) == 80.0
    assert max_rps(1, 3) == 333.3
    with pytest.raises(ValueError):
        max_rps(1, 0)


def test_replicas():
    assert replicas_needed(500, 120) == 6
    assert replicas_needed(84, 120) == 1
    assert replicas_needed(84.01, 120) == 2
    assert replicas_needed(0, 120) == 1
    assert replicas_needed(100, 100, headroom=0) == 1
    with pytest.raises(ValueError):
        replicas_needed(10, 10, headroom=1)


def test_utilization():
    assert utilization(70, 4, 50) == 0.875
    assert utilization(100, 4, 50) == 1.25
