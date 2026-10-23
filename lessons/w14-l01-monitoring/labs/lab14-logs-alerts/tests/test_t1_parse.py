from logs import filter_logs, parse_line

LINES = [
    '{"ts": "2027-02-09T10:00:00Z", "level": "INFO", "msg": "start", "room": "R1"}',
    'Traceback (most recent call last):',
    '{"ts": "2027-02-09T10:00:01Z", "level": "ERROR", "msg": "ws closed", "room": "R1", "code": 1006}',
    '{"ts": "2027-02-09T10:00:02Z", "level": "DEBUG", "msg": "tick", "room": "R2"}',
    '[1, 2, 3]',
    '{"level": "INFO", "msg": "нет ts"}',
    '{"ts": "2027-02-09T10:00:03Z", "level": "WARNING", "msg": "slow tick", "room": "R2", "ms": 180}',
    '{"ts": "2027-02-09T10:00:04Z", "level": "NOTICE", "msg": "чужой уровень"}',
    '',
]


def test_parse_line():
    assert parse_line(LINES[0])["room"] == "R1"
    for bad in (LINES[1], LINES[4], LINES[5], LINES[7], LINES[8], '{"ts": 1, "level": "INFO"'):
        assert parse_line(bad) is None


def test_filter_level():
    assert [r["msg"] for r in filter_logs(LINES)] == ["start", "ws closed", "slow tick"]
    assert [r["msg"] for r in filter_logs(LINES, "WARNING")] == ["ws closed", "slow tick"]
    assert len(filter_logs(LINES, "DEBUG")) == 4


def test_filter_fields():
    assert [r["msg"] for r in filter_logs(LINES, "DEBUG", room="R2")] == ["tick", "slow tick"]
    assert filter_logs(LINES, "ERROR", room="R1", code=1006)[0]["msg"] == "ws closed"
    assert filter_logs(LINES, room="R3") == []
