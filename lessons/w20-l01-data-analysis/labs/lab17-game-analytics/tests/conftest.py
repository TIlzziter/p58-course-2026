import sqlite3
from pathlib import Path

import pandas as pd
import pytest

SMALL = """ts,user_id,event,match_id,side,result,duration_s,score
2027-03-01T10:00:00Z,1,session_start,,,,,
2027-03-01T10:01:00Z,1,match_start,1,first,,,
2027-03-01T10:01:00Z,2,match_start,1,second,,,
2027-03-01T10:02:00Z,1,match_end,1,first,win,60,10
2027-03-01T10:02:00Z,2,match_end,1,second,loss,60,0
2027-03-01T10:02:00Z,2,match_end,1,second,loss,60,0
2027-03-01T09:00:00Z,2,session_start,,,,,
2027-03-01T23:59:59Z,3,debug_ping,,,,,
2027-03-02T08:00:00Z,1,session_start,,,,,
2027-03-02T08:01:00Z,1,match_end,2,second,draw,120,3
2027-03-02T08:01:00Z,3,match_end,2,first,draw,120,3
2027-03-02T08:05:00Z,1,match_end,3,first,win,30,10
2027-03-02T08:05:00Z,3,match_end,3,second,loss,30,0
2027-03-02T09:00:00Z,3,session_start,,,,,
2027-03-04T12:00:00Z,2,session_start,,,,,
2027-03-04T12:10:00Z,2,match_end,4,first,loss,90,0
2027-03-04T12:10:00Z,4,match_end,4,second,win,90,10
2027-03-04T13:00:00Z,4,session_start,,,,,
2027-03-08T10:00:00Z,1,session_start,,,,,
"""


@pytest.fixture
def small_csv(tmp_path) -> Path:
    p = tmp_path / "events.csv"
    p.write_text(SMALL)
    return p


@pytest.fixture
def big_csv() -> Path:
    p = Path(__file__).parent.parent / "data" / "events.csv"
    if not p.exists():
        from gen_data import generate, write
        write(p, generate())
    return p


@pytest.fixture
def small_df(small_csv):
    """Эталонная загрузка (не зависит от задачи 1), чтобы задачи 2–7 проверялись отдельно."""
    df = pd.read_csv(small_csv)
    df["ts"] = pd.to_datetime(df["ts"], utc=True)
    df = df.drop_duplicates()
    df = df[df["event"] != "debug_ping"]
    return df.sort_values("ts", kind="stable").reset_index(drop=True)


@pytest.fixture
def small_db(small_csv):
    conn = sqlite3.connect(":memory:")
    df = pd.read_csv(small_csv).drop_duplicates()
    df.to_sql("events", conn, index=False)
    yield conn
    conn.close()
