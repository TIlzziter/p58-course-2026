import pytest
from clock import ClockSync


def test_single_sample():
    c = ClockSync()
    c.add(sent=1000, server=5050, received=1100)      # RTT 100, сервер в середине пути
    assert c.offset == 4000 and c.rtt == 100 and c.server_now(2000) == 6000


def test_min_rtt_wins():
    c = ClockSync()
    c.add(0, 4100, 300)        # RTT 300, оценка 3950 — шумная
    c.add(1000, 5020, 1040)    # RTT 40, оценка 4000
    c.add(2000, 6200, 2200)    # RTT 200
    assert c.offset == 4000 and c.rtt == 40


def test_window():
    c = ClockSync(keep=2)
    c.add(0, 4010, 20)          # лучший, но вытеснится
    c.add(100, 4200, 300)
    c.add(400, 4500, 600)
    assert c.rtt == 200 and c.offset == 4000


def test_tie_prefers_fresh():
    c = ClockSync()
    c.add(0, 4050, 100)
    c.add(1000, 5060, 1100)
    assert c.offset == 4010


def test_errors():
    with pytest.raises(LookupError):
        ClockSync().offset
    with pytest.raises(ValueError):
        ClockSync().add(10, 0, 5)
