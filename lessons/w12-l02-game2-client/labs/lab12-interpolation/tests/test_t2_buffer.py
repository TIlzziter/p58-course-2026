from interp import SnapshotBuffer


def buf(*times, size=32):
    b = SnapshotBuffer(size)
    for t in times:
        b.add(t, {"t": t})
    return b


def test_sample_between():
    b = buf(0, 100, 200)
    prev, nxt, a = b.sample(150)
    assert prev == {"t": 100} and nxt == {"t": 200} and a == 0.5


def test_sample_exact_and_edges():
    b = buf(0, 100, 200)
    assert b.sample(100)[0] == {"t": 100} and b.sample(100)[2] == 0
    assert b.sample(-50) == ({"t": 0}, {"t": 0}, 0.0)
    assert b.sample(999) == ({"t": 200}, {"t": 200}, 1.0)
    assert SnapshotBuffer().sample(0) is None


def test_out_of_order_inserted_sorted():
    b = buf(0, 200, 100)
    assert b.times == [0, 100, 200]
    assert b.sample(50)[1] == {"t": 100}


def test_duplicate_ignored():
    b = buf(0, 100)
    assert b.add(100, {"t": "again"}) is False and b.sample(100)[0] == {"t": 100}


def test_size_limit_and_too_old():
    b = buf(0, 100, 200, 300, size=3)
    assert b.times == [100, 200, 300]
    assert b.add(50, {"t": 50}) is False          # старше самого старого в полном буфере
    assert b.add(250, {"t": 250}) is True and b.times == [200, 250, 300]
