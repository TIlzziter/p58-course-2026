from incident import incident_summary


def traffic():
    rs = []
    for minute in range(6):                     # 6 минут, по 10 запросов
        for i in range(10):
            bad = minute in (2, 3) and i < (4 if minute == 2 else 3)
            path = "/ws/game" if i % 2 == 0 else "/api/rating"
            rs.append({"ts": 6000 + minute * 60 + i * 5, "status": 502 if bad else 200, "path": path})
    rs.append({"ts": 6000 + 4 * 60 + 1, "status": 500, "path": "/api/rating"})   # одна ошибка — 1/11, не инцидент
    return rs


def test_summary():
    assert incident_summary(traffic()) == {"start": 6120, "end": 6240, "errors": 7, "top_path": "/ws/game",
                                           "bad_minutes": 2}


def test_none_and_min_requests():
    assert incident_summary([{"ts": 0, "status": 200, "path": "/"}]) is None
    few = [{"ts": i, "status": 500, "path": "/x"} for i in range(4)]
    assert incident_summary(few) is None
    assert incident_summary(few, min_requests=4)["errors"] == 4


def test_tie_by_name():
    rs = [{"ts": i, "status": 500, "path": p} for i, p in enumerate(["/b", "/a", "/b", "/a", "/c"])]
    assert incident_summary(rs)["top_path"] == "/a"
