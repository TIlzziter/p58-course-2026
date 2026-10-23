import pytest
from merge import merge_logs
from query import parse_query, run_query, stats
from tasks import (
    burn_alert,
    counter_rate,
    dedupe_alerts,
    downtime,
    error_budget,
    flaky,
    junit_summary,
    min_tests,
    missing_ranges,
    parse_access,
    timeline,
    top_ips,
    trace,
    uptime,
)

X = '''<testsuites><testsuite name="pytest">
<testcase classname="t" name="a" time="0.010"/>
<testcase classname="t" name="b" time="0.200"><failure message="assert 1 == 2"/></testcase>
<testcase classname="t" name="c" time="0.005"><skipped/></testcase>
<testcase classname="t" name="d" time="1.300"><error message="fixture"/></testcase>
<testcase classname="t" name="e" time="0.020"/>
</testsuite></testsuites>'''
LINE = ('10.0.0.5 - - [09/Feb/2027:10:00:01 +0300] "GET /api/top HTTP/1.1" 200 512 "-" '
        '"curl/8.5"')
RECS = [{"level": "INFO", "path": "/ws", "ms": 20, "room": "R1"},
        {"level": "ERROR", "path": "/ws", "ms": 350, "room": "R1"},
        {"level": "WARNING", "path": "/api", "ms": 120, "room": "R2"},
        {"level": "ERROR", "path": "/api", "ms": 900},
        {"level": "DEBUG", "path": "/ws", "ms": 5, "room": "R1"}]


def test_a1():
    assert junit_summary(X) == {"passed": 2, "failed": 1, "errors": 1, "skipped": 1, "time": 1.535}
    assert junit_summary('<testsuite name="x"></testsuite>') == {"passed": 0, "failed": 0, "errors": 0,
                                                                 "skipped": 0, "time": 0.0}


def test_a2():
    runs = [{"a": True, "b": True, "c": False}, {"a": True, "b": False, "c": False}, {"a": True, "b": True}]
    assert flaky(runs) == ["b"]
    assert flaky([{"x": False, "y": True}, {"y": False, "x": True}]) == ["x", "y"]
    assert flaky([]) == []


def test_a3():
    assert missing_ranges({1, 2, 6, 7, 10}, 12, skip={4}) == "3, 5, 8-9, 11-12"
    assert missing_ranges(set(range(1, 6)), 5) == ""
    assert missing_ranges(set(), 3) == "1-3"


def test_a4():
    k = {"m1": {"t1", "t3"}, "m2": {"t2"}, "m3": {"t3"}, "m4": set(), "m5": {"t1", "t2"}}
    assert min_tests(k) == ["t2", "t3"]
    assert min_tests({"m": set()}) == [] and min_tests({}) == []
    assert min_tests({"a": {"x", "y"}, "b": {"y", "z"}, "c": {"x", "z"}}) == ["x", "y"]
    greedy_trap = {"m1": {"tA", "tC"}, "m2": {"tA", "tC"}, "m3": {"tA"},
                   "m4": {"tB", "tC"}, "m5": {"tB", "tC"}, "m6": {"tB"}}
    assert min_tests(greedy_trap) == ["tA", "tB"]


def test_b1():
    assert parse_access(LINE) == {"ip": "10.0.0.5", "time": "09/Feb/2027:10:00:01 +0300", "method": "GET",
                                  "path": "/api/top", "status": 200, "bytes": 512,
                                  "ua": "curl/8.5"}
    assert parse_access(LINE.replace(" 512 ", " - "))["bytes"] == 0
    assert parse_access("мусор") is None


def test_b2():
    lines = [LINE, LINE.replace("10.0.0.5", "10.0.0.7"), LINE, "мусор",
             LINE.replace("10.0.0.5", "10.0.0.2"), LINE.replace("10.0.0.5", "10.0.0.7")]
    assert top_ips(lines, 2) == [("10.0.0.5", 2), ("10.0.0.7", 2)]
    assert top_ips(lines, 10)[-1] == ("10.0.0.2", 1)


def test_b3():
    r = [{"ts": 3, "service": "bot", "rid": "r1", "msg": "reply sent"},
         {"ts": 1, "service": "nginx", "rid": "r1", "msg": "GET /ws"},
         {"ts": 2, "service": "api", "rid": "r2", "msg": "other"},
         {"ts": 2, "service": "api", "rid": "r1", "msg": "join R1"},
         {"ts": 2, "service": "redis", "rid": "r1", "msg": "SET room"},
         {"ts": 9, "service": "api", "msg": "нет rid"}]
    assert trace(r, "r1") == ["nginx: GET /ws", "api: join R1", "redis: SET room", "bot: reply sent"]
    assert trace(r, "zzz") == []


def test_c1():
    assert counter_rate([(0, 100), (10, 150), (20, 20), (30, 40)]) == pytest.approx(3.0)
    assert counter_rate([(0, 5), (60, 5)]) == 0
    assert counter_rate([(0, 5)]) is None


def test_c2():
    assert uptime([True, True, False, False, False, True, False, True], 30) == (50.0, 90)
    assert uptime([True] * 3, 60) == (100.0, 0)
    assert uptime([True, False, True], 10) == (66.67, 10)
    with pytest.raises(ValueError):
        uptime([], 10)


def test_c3():
    assert error_budget(10000, 20, 0.995) == (50, 30, 0.4)
    assert error_budget(200000, 1500, 0.999) == (200, -1300, 7.5)
    assert error_budget(1000, 0, 0.999) == (1, 1, 0.0)
    assert error_budget(100000, 25, 0.9995) == (50, 25, 0.5)


def test_c4():
    mins = [(100, 0)] * 30 + [(100, 30)] * 10
    assert burn_alert(mins, 0.999) == 31
    assert burn_alert([(100, 0)] * 100, 0.999) is None
    assert burn_alert([(100, 2)], 0.999) == 0                  # 2 % при бюджете 0,1 % — сразу
    assert burn_alert([(0, 0), (10, 1)], 0.99, factor=5, long=2, short=1) == 1


def test_d1():
    assert downtime([(10, 20), (15, 30), (40, 45), (30, 35)]) == ([(10, 35), (40, 45)], 30)
    assert downtime([]) == ([], 0)
    assert downtime([(0, 10), (2, 3)]) == ([(0, 10)], 10)


def test_d2():
    a = [(0, "5xx"), (30, "5xx"), (65, "5xx"), (10, "slow"), (70, "5xx"), (130, "5xx")]
    assert dedupe_alerts(a, 60) == [(0, "5xx"), (10, "slow"), (65, "5xx"), (130, "5xx")]
    assert dedupe_alerts([(0, "x"), (60, "x")], 60) == [(0, "x"), (60, "x")]


def test_d3():
    ev = [(1000, "починили"), (700, "алерт"), (640, "деплой v0.8"), (4300, "постмортем")]
    assert timeline(ev) == ["T+00:00 деплой v0.8", "T+01:00 алерт", "T+06:00 починили", "T+1:01:00 постмортем"]
    assert timeline([]) == []
    assert timeline([(5, "b"), (5, "a")]) == ["T+00:00 b", "T+00:00 a"]


def test_e4a():
    assert parse_query("level>=WARNING room=R1 ms>100") == [("level", ">=", "WARNING"), ("room", "=", "R1"),
                                                            ("ms", ">", 100)]
    assert parse_query("") == [] and parse_query("k=1.5 x!=-3") == [("k", "=", 1.5), ("x", "!=", -3)]
    for bad in ("level>=LOUD", "ms>>1", "room", "=5"):
        with pytest.raises(ValueError):
            parse_query(bad)


def test_e4b():
    assert run_query(RECS, "level>=WARNING room=R1 ms>100") == [RECS[1]]
    assert run_query(RECS, "level<INFO") == [RECS[4]]
    assert run_query(RECS, "room!=R1") == [RECS[2]]                # нет поля — условие ложно
    assert run_query(RECS, "path>5") == []                         # строка и число не сравниваются
    assert len(run_query(RECS, "")) == 5


def test_e4c():
    assert stats(RECS, "level>=INFO | count by path") == {"/api": 2, "/ws": 2}
    assert stats(RECS, "| avg ms by path") == {"/api": 510.0, "/ws": 125.0}
    assert stats(RECS, "path=/ws | max ms by level") == {"DEBUG": 5, "ERROR": 350, "INFO": 20}
    assert stats(RECS, "| count by room") == {"R1": 3, "R2": 1}
    with pytest.raises(ValueError):
        stats(RECS, "| sum ms by path")


def test_e5():
    a = ['{"ts": 1, "msg": "api start"}', '{"ts": 5, "msg": "api error"}', "Traceback (most recent call last):",
         "  ValueError: boom"]
    b = ['{"ts": 2, "msg": "bot start"}', '{"ts": 5, "msg": "bot retry"}']
    assert merge_logs([a, b]) == [a[0], b[0], a[1], a[2], a[3], b[1]]
    assert merge_logs([["мусор до начала", '{"ts": 1}'], []]) == ['{"ts": 1}']
    assert merge_logs([[f'{{"ts": {t}}}' for t in (3, 1)]]) == ['{"ts": 1}', '{"ts": 3}']
