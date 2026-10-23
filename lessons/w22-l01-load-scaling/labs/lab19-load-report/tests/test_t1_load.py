from loadlog import Request, load_log


def test_small(small_csv):
    reqs, skipped = load_log(small_csv)
    assert skipped == 3
    assert [r.ts for r in reqs] == [0.0, 0.5, 1.0, 2.0, 3.0, 3.5]
    assert reqs[0] == Request(0.0, "GET /a", 200, 30.0)
    assert reqs[-1].status == 0


def test_types(small_csv):
    reqs, _ = load_log(small_csv)
    r = reqs[2]
    assert isinstance(r.status, int) and isinstance(r.ms, float) and r.name == "GET /b"


def test_negative_and_empty_name_skipped(tmp_path):
    p = tmp_path / "x.csv"
    p.write_text("ts,name,status,ms\n1,GET /a,200,-1\n2, ,200,3\n3,GET /a,200,3\n", encoding="utf-8")
    reqs, skipped = load_log(p)
    assert skipped == 2 and len(reqs) == 1


def test_real_files(before_path, after_path):
    for p in (before_path, after_path):
        reqs, skipped = load_log(p)
        assert len(reqs) == 6000 and skipped == 4
        assert all(a.ts <= b.ts for a, b in zip(reqs, reqs[1:]))
