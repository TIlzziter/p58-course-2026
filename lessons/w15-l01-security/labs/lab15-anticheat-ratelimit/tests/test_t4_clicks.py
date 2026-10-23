import random

from anticheat import click_audit


def human(n, seed=1):
    rnd = random.Random(seed)
    t, out = 0, []
    for _ in range(n):
        t += rnd.randint(90, 250)
        out.append(t)
    return out


def test_honest():
    s = human(40)
    assert click_audit(s, 40) == []
    assert click_audit([], 0) == [] and click_audit([5], 1) == []


def test_count_mismatch():
    assert click_audit(human(40), 400) == ["count_mismatch"]


def test_too_fast():
    burst = [1000 + 60 * i for i in range(17)]          # 17 нажатий за 960 мс
    assert "too_fast" in click_audit(burst, 17)
    edge = [1000 + 66 * i for i in range(16)]           # 16 нажатий, но от первого до 16-го 990 мс
    assert "too_fast" in click_audit(edge, 16)
    ok = [1000 + 67 * i for i in range(16)]             # 16-е через 1005 мс — уже другое окно
    assert "too_fast" not in click_audit(ok, 16)


def test_robotic():
    bot = [100 * i for i in range(30)]
    assert click_audit(bot, 30) == ["robotic"]
    assert click_audit(bot[:9], 9) == []                # мало данных — не судим
    jitter = [100 * i + (i % 2) * 7 for i in range(30)]  # интервалы 107/93: разброс 7 мс
    assert click_audit(jitter, 30) == []


def test_all_reasons_and_unsorted():
    bot = [50 * i for i in range(30)]
    assert click_audit(bot, 99) == ["count_mismatch", "too_fast", "robotic"]
    assert click_audit([10, 5, 20], 3) == ["unsorted"]
