from analytics import balance, load_events


def test_small(small_df):
    assert balance(small_df) == {"games": 4, "first_wins": 2, "second_wins": 1, "draws": 1,
                                 "first_win_rate": 0.667, "p_value": 1.0}


def test_big(big_csv):
    b = balance(load_events(big_csv))
    assert b["games"] == b["first_wins"] + b["second_wins"] + b["draws"]
    assert b["first_win_rate"] > 0.55
    assert b["p_value"] < 0.001                                   # в генераторе перекос 47 % против 33 %


def test_empty(small_df):
    b = balance(small_df[small_df["event"] == "session_start"])
    assert b["games"] == 0 and b["first_win_rate"] is None and b["p_value"] == 1.0
