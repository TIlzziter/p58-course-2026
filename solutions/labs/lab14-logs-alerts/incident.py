"""Задача 7*. Сводка инцидента по логам запросов."""
from collections import Counter


def incident_summary(records: list[dict], ratio: float = 0.1, min_requests: int = 5) -> dict | None:
    """Минуты, где доля 5xx > ratio и запросов ≥ min_requests, — «плохие».
    Инцидент — от первой до последней плохой минуты. None, если плохих нет."""
    by_min: dict[int, list[dict]] = {}
    for r in records:
        by_min.setdefault(int(r["ts"]) // 60 * 60, []).append(r)
    bad = sorted(m for m, rs in by_min.items()
                 if len(rs) >= min_requests and sum(x["status"] >= 500 for x in rs) / len(rs) > ratio)
    if not bad:
        return None
    start, end = bad[0], bad[-1] + 60
    errs = [r for r in records if start <= r["ts"] < end and r["status"] >= 500]
    paths = Counter(r["path"] for r in errs)
    top = min(paths, key=lambda p: (-paths[p], p))
    return {"start": start, "end": end, "errors": len(errs), "top_path": top, "bad_minutes": len(bad)}
