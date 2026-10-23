"""Генератор учебных журналов нагрузочного теста: data/before.csv и data/after.csv.

Сценарий: 60 секунд, ~100 RPS. «До» — таблица лидеров без индекса и одна реплика. «После» — индекс
и кэш лидеров в Redis, но новый эндпоинт профиля иногда падает. В файлах есть несколько битых строк.
Запуск: python gen_data.py (результат всегда одинаковый — seed фиксирован).
"""
import csv
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent

# эндпоинт: (доля запросов, медиана мс, «хвост» мс, вероятность 5xx)
BEFORE = {
    "GET /api/rooms": (0.35, 18, 60, 0.0),
    "POST /api/rooms/{id}/move": (0.40, 25, 90, 0.002),
    "GET /api/leaderboard": (0.15, 420, 1500, 0.02),
    "GET /api/profile": (0.10, 30, 80, 0.0),
}
AFTER = {
    "GET /api/rooms": (0.35, 19, 62, 0.0),
    "POST /api/rooms/{id}/move": (0.40, 22, 70, 0.002),
    "GET /api/leaderboard": (0.15, 9, 40, 0.0),
    "GET /api/profile": (0.10, 34, 95, 0.03),
}


def generate(profile, seed, path, seconds=60, rps=100):
    rng = random.Random(seed)
    names = list(profile)
    shares = [profile[n][0] for n in names]
    rows = []
    for k in range(seconds * rps):
        ts = round(k / rps + rng.random() / rps, 3)
        name = rng.choices(names, shares)[0]
        _, med, tail, p_err = profile[name]
        ms = rng.lognormvariate(0, 0.35) * med
        if rng.random() < 0.04:
            ms = rng.uniform(med, tail * 1.5)
        status = 200
        if rng.random() < p_err:
            status = rng.choice([500, 502, 503, 0])
        rows.append([f"{ts:.3f}", name, status, f"{ms:.1f}"])
    for bad in (["", "GET /api/rooms", "200", "12.0"], ["5.5", "GET /api/rooms", "ok", "10"],
                ["7.25", "GET /api/rooms", "200", "-3"], ["9.1", "", "200", "5"]):
        rows.insert(rng.randrange(len(rows)), bad)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ts", "name", "status", "ms"])
        w.writerows(rows)


if __name__ == "__main__":
    (HERE / "data").mkdir(exist_ok=True)
    generate(BEFORE, 58, HERE / "data" / "before.csv")
    generate(AFTER, 59, HERE / "data" / "after.csv")
