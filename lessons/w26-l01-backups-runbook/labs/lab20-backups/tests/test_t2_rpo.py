from datetime import datetime, timedelta

import pytest
from rpo import data_loss, meets_targets, rto_estimate, worst_rpo

B = [datetime(2027, 4, 26, h) for h in (0, 6, 12, 18)]


def test_data_loss():
    assert data_loss(B, datetime(2027, 4, 26, 17, 30)) == timedelta(hours=5, minutes=30)
    assert data_loss(B, datetime(2027, 4, 26, 6)) == timedelta(0)
    assert data_loss(B, datetime(2027, 4, 25, 23)) is None


def test_worst_rpo():
    assert worst_rpo(B) == timedelta(hours=6)
    assert worst_rpo([B[3], B[0], B[1]]) == timedelta(hours=12)
    with pytest.raises(ValueError):
        worst_rpo(B[:1])


def test_rto():
    assert rto_estimate(1200, 40, [60, 120, 30]) == 240.0
    assert rto_estimate(10, 3, []) == 3.3
    with pytest.raises(ValueError):
        rto_estimate(10, 0, [])


def test_targets():
    r = meets_targets(B, timedelta(hours=4), 300, 1200, 40, [60, 120, 30])
    assert r == {"rpo_ok": False, "rto_ok": True, "worst_rpo_min": 360.0, "rto_s": 240.0}
    assert meets_targets(B, timedelta(hours=6), 200, 1200, 40, [60])["rpo_ok"] is True
