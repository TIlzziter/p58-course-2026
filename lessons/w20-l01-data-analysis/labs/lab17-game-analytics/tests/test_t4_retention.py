import math
from datetime import date

from analytics import load_events, retention


def test_small(small_df):
    r = retention(small_df, days=(1, 3, 7))
    assert list(r.columns) == ["size", "d1", "d3", "d7"]
    assert list(r.index) == [date(2027, 3, 1), date(2027, 3, 2), date(2027, 3, 4)]
    assert list(r["size"]) == [2, 1, 1]
    c1 = r.loc[date(2027, 3, 1)]
    assert c1["d1"] == 0.5 and c1["d3"] == 0.5 and c1["d7"] == 0.5
    assert r.loc[date(2027, 3, 2), "d1"] == 0.0
    assert math.isnan(r.loc[date(2027, 3, 2), "d7"])               # 9 марта ещё не наступило
    assert r.loc[date(2027, 3, 4), "d3"] == 0.0


def test_big(big_csv):
    df = load_events(big_csv)
    r = retention(df)
    assert r["size"].sum() == df["user_id"].nunique()
    assert (r["d1"].dropna().between(0, 1)).all()
    last = df["ts"].dt.date.max()
    late = [c for c in r.index if (last - c).days < 7]
    assert r.loc[late, "d7"].isna().all()
    assert r.drop(late)["d7"].notna().all()
