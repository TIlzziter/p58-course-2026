"""Генератор учебных данных: события игры «крестики-нолики» за 3 недели. Готов, менять не нужно.

python gen_data.py            → data/events.csv
У первого хода специально есть преимущество, часть строк — дубликаты, есть «мусорные» события.
"""
import csv
import random
from datetime import UTC, datetime, timedelta
from pathlib import Path

START = datetime(2027, 3, 1, tzinfo=UTC)
FIELDS = ["ts", "user_id", "event", "match_id", "side", "result", "duration_s", "score"]


def generate(seed: int = 58, users: int = 120, days: int = 21) -> list[dict]:
    rnd = random.Random(seed)
    rows, match_id = [], 0
    for uid in range(1, users + 1):
        first = rnd.randrange(days)
        loyalty = rnd.random()
        for d in range(first, days):
            if d > first and rnd.random() > 0.15 + 0.6 * loyalty:
                continue
            t = START + timedelta(days=d, hours=rnd.randint(8, 21), minutes=rnd.randrange(60))
            rows.append({"ts": t, "user_id": uid, "event": "session_start"})
            for _ in range(rnd.randint(0, 4)):
                match_id += 1
                opp = rnd.randint(1, users)
                dur = round(rnd.lognormvariate(4.2, 0.5), 1)
                side = rnd.choice(["first", "second"])
                r = rnd.random()
                res_first = "win" if r < 0.47 else "loss" if r < 0.80 else "draw"
                me = res_first if side == "first" else {"win": "loss", "loss": "win", "draw": "draw"}[res_first]
                t += timedelta(seconds=rnd.randint(5, 60))
                for u, s, res in ((uid, side, me), (opp, "second" if side == "first" else "first",
                                                    {"win": "loss", "loss": "win", "draw": "draw"}[me])):
                    rows.append({"ts": t, "user_id": u, "event": "match_start", "match_id": match_id, "side": s})
                    rows.append({"ts": t + timedelta(seconds=dur), "user_id": u, "event": "match_end",
                                 "match_id": match_id, "side": s, "result": res, "duration_s": dur,
                                 "score": {"win": 10, "draw": 3, "loss": 0}[res]})
                t += timedelta(seconds=dur)
            if rnd.random() < 0.05:
                rows.append({"ts": t, "user_id": uid, "event": "debug_ping"})
    for r in rnd.sample(rows, len(rows) // 50):
        rows.append(dict(r))
    rnd.shuffle(rows)
    for r in rows:
        r["ts"] = r["ts"].strftime("%Y-%m-%dT%H:%M:%SZ")
    return rows


def write(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    out = Path(__file__).parent / "data" / "events.csv"
    write(out, generate())
    print(out)
