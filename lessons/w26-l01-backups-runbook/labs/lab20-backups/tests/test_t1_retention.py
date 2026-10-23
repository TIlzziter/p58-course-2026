from datetime import datetime, timedelta

from retention import keep, to_delete

NOW = datetime(2027, 4, 26, 12, 0)  # понедельник
NIGHTLY = [datetime(2027, 4, 26, 3, 0) - timedelta(days=i) for i in range(120)]


def test_only_daily():
    k = keep(NIGHTLY, NOW, daily=7, weekly=0, monthly=0)
    assert k == set(NIGHTLY[:7])


def test_weekly_takes_newest_of_week():
    k = keep(NIGHTLY, NOW, daily=0, weekly=3, monthly=0)
    # текущая неделя — только понедельник 26.04; прошлые — воскресенья 25.04 и 18.04
    assert k == {datetime(2027, 4, 26, 3), datetime(2027, 4, 25, 3), datetime(2027, 4, 18, 3)}


def test_monthly():
    k = keep(NIGHTLY, NOW, daily=0, weekly=0, monthly=4)
    assert k == {datetime(2027, 4, 26, 3), datetime(2027, 3, 31, 3), datetime(2027, 2, 28, 3),
                 datetime(2027, 1, 31, 3)}


def test_full_gfs_count_and_delete():
    k = keep(NIGHTLY, NOW)
    # 7 дней (20–26.04) + недели: 18.04, 11.04 + месяцы: 31.03, 28.02, 31.01, 31.12 (ноября в истории нет)
    assert len(k) == 13
    d = to_delete(NIGHTLY, NOW)
    assert len(d) == 120 - len(k) and d == sorted(d) and not set(d) & k


def test_newest_always_kept_and_future_ignored():
    old = [datetime(2026, 1, 1)]
    assert keep(old, NOW, daily=1, weekly=0, monthly=0) == set(old)
    future = datetime(2027, 4, 27)
    assert future not in keep([*old, future], NOW) and to_delete([*old, future], NOW) == []
    assert keep([], NOW) == set()


def test_several_per_day():
    b = [datetime(2027, 4, 26, h) for h in (1, 5, 9)]
    assert keep(b, NOW, daily=7, weekly=0, monthly=0) == {datetime(2027, 4, 26, 9)}
