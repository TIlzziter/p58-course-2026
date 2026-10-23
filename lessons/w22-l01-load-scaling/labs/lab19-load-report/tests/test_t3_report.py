from loadlog import compare, endpoint_stats, load_log, render_markdown


def s(p95, fail=0.0):
    return {"p95": p95, "fail_rate": fail}


def test_verdicts():
    before = {"a": s(100), "b": s(100), "c": s(100), "d": s(100, 0.0), "only_before": s(1)}
    after = {"a": s(50), "b": s(111), "c": s(105), "d": s(60, 0.02), "only_after": s(1)}
    rows = compare(before, after)
    assert [r["name"] for r in rows] == ["a", "b", "c", "d"]
    assert [r["verdict"] for r in rows] == ["лучше", "хуже", "без изменений", "хуже"]
    assert rows[0]["change"] == -0.5 and rows[1]["change"] == 0.11


def test_threshold_boundary():
    rows = compare({"a": s(100)}, {"a": s(110)}, threshold=0.1)
    assert rows[0]["verdict"] == "без изменений"


def test_markdown_format():
    rows = compare({"GET /x": s(200, 0.005)}, {"GET /x": s(80.5, 0)})
    md = render_markdown(rows).splitlines()
    assert md[0] == "| Эндпоинт | p95 до, мс | p95 после, мс | Изменение | Ошибки до | Ошибки после | Вывод |"
    assert md[1] == "|---|---|---|---|---|---|---|"
    assert md[2] == "| GET /x | 200 | 80.5 | \u221260 % | 0.5 % | 0.0 % | лучше |"
    md = render_markdown(compare({"a": s(10)}, {"a": s(10)})).splitlines()
    assert md[2] == "| a | 10 | 10 | 0 % | 0.0 % | 0.0 % | без изменений |"


def test_real_report(before_path, after_path):
    b = endpoint_stats(load_log(before_path)[0])
    a = endpoint_stats(load_log(after_path)[0])
    verdicts = {r["name"]: r["verdict"] for r in compare(b, a)}
    assert verdicts == {"GET /api/leaderboard": "лучше", "GET /api/profile": "хуже",
                        "GET /api/rooms": "без изменений", "POST /api/rooms/{id}/move": "лучше"}
    assert "| GET /api/profile | 58.5 | 69.2 | +18 % | 0.0 % | 3.4 % | хуже |" in render_markdown(compare(b, a))
