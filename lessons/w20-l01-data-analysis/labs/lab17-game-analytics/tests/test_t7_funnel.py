import pandas as pd
from analytics import funnel, load_events


def test_small(small_df):
    # у игроков 3 и 4 матч закончился раньше, чем началась их сессия, — не засчитываем
    assert funnel(small_df, ["session_start", "match_end"]) == [4, 2]
    assert funnel(small_df, ["session_start", "match_start", "match_end"]) == [4, 2, 2]
    assert funnel(small_df, ["match_end", "session_start"]) == [4, 4]


def test_order_matters():
    t = pd.Timestamp("2027-03-01T10:00:00Z")
    df = pd.DataFrame([
        {"ts": t, "user_id": 1, "event": "b"},
        {"ts": t + pd.Timedelta(minutes=1), "user_id": 1, "event": "a"},
        {"ts": t + pd.Timedelta(minutes=2), "user_id": 2, "event": "a"},
        {"ts": t + pd.Timedelta(minutes=3), "user_id": 2, "event": "b"},
        {"ts": t + pd.Timedelta(minutes=4), "user_id": 2, "event": "c"},
        {"ts": t + pd.Timedelta(minutes=5), "user_id": 3, "event": "c"},
    ])
    assert funnel(df, ["a", "b", "c"]) == [2, 1, 1]
    assert funnel(df, ["c"]) == [2]
    assert funnel(df, ["x", "a"]) == [0, 0]


def test_big(big_csv):
    f = funnel(load_events(big_csv), ["session_start", "match_start", "match_end"])
    assert f[0] >= f[1] >= f[2] > 0
