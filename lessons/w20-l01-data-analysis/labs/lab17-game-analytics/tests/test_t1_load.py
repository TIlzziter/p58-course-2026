import pandas as pd
from analytics import load_events


def test_small(small_csv):
    df = load_events(small_csv)
    assert len(df) == 17                                   # 19 строк − дубликат − debug_ping
    assert str(df["ts"].dt.tz) == "UTC"
    assert df["ts"].is_monotonic_increasing
    assert list(df.index) == list(range(17))
    assert df["user_id"].dtype.kind == "i"
    assert "debug_ping" not in set(df["event"])
    assert df.iloc[0]["event"] == "session_start" and df.iloc[0]["user_id"] == 2   # 09:00 раньше 10:00


def test_stable_order(small_csv):
    df = load_events(small_csv)
    same = df[df["ts"] == pd.Timestamp("2027-03-01T10:02:00Z")]
    assert list(same["user_id"]) == [1, 2]


def test_big(big_csv):
    df = load_events(big_csv)
    raw = pd.read_csv(big_csv)
    assert len(df) < len(raw)
    assert not df.duplicated().any()
    assert set(df["event"]) == {"session_start", "match_start", "match_end"}
