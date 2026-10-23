from datetime import date

import pandas as pd
from analytics import match_stats


def test_small(small_df):
    m = match_stats(small_df)
    assert list(m.columns) == ["matches", "median_s", "p90_s"]
    assert list(m.index) == [date(2027, 3, 1), date(2027, 3, 2), date(2027, 3, 4)]
    assert list(m["matches"]) == [2, 4, 2]                       # по событию на игрока
    assert m.loc[date(2027, 3, 2), "median_s"] == 75.0
    assert m.loc[date(2027, 3, 2), "p90_s"] == 120.0
    assert m.loc[date(2027, 3, 1), "p90_s"] == 60.0


def test_quantile_interpolation():
    rows = [{"ts": pd.Timestamp("2027-03-01T10:00:00Z") + pd.Timedelta(minutes=i), "user_id": i,
             "event": "match_end", "duration_s": d} for i, d in enumerate([10, 20, 30, 40, 100])]
    m = match_stats(pd.DataFrame(rows))
    assert m.iloc[0]["median_s"] == 30.0 and m.iloc[0]["p90_s"] == 76.0
