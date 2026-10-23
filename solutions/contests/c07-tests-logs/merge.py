"""E5*: слияние логов нескольких сервисов по времени."""
import heapq
import json


def _records(lines):
    """Склеить строки без ts (трейсбеки) с предыдущей записью: [(ts, [строки])]."""
    recs = []
    for line in lines:
        try:
            ts = json.loads(line)["ts"]
        except (json.JSONDecodeError, KeyError, TypeError):
            ts = None
        if ts is None:
            if recs:
                recs[-1][1].append(line)
            continue                             # строки до первой записи выбрасываем
        recs.append((ts, [line]))
    return recs


def merge_logs(files: list[list[str]]) -> list[str]:
    heap = []
    for fi, lines in enumerate(files):
        for li, (ts, block) in enumerate(_records(lines)):
            heap.append((ts, fi, li, block))
    heapq.heapify(heap)
    out = []
    while heap:
        out.extend(heapq.heappop(heap)[3])
    return out
