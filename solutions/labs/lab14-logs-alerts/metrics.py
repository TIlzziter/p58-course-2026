"""Задачи 3–4. Метрики RED и гистограмма."""
import math


def percentile(values, q):
    s = sorted(values)
    return s[max(math.ceil(q * len(s)) - 1, 0)]


def red(records: list[dict], start: float, end: float) -> dict | None:
    """Rate, Errors, Duration по запросам с ts в [start, end)."""
    win = [r for r in records if start <= r["ts"] < end]
    if not win:
        return None
    ms = [r["ms"] for r in win]
    return {
        "rate": len(win) / (end - start),
        "errors": sum(r["status"] >= 500 for r in win) / len(win),
        "p50": percentile(ms, 0.5),
        "p95": percentile(ms, 0.95),
    }


class Histogram:
    def __init__(self, name: str, buckets: list[float]):
        if list(buckets) != sorted(set(buckets)) or not buckets:
            raise ValueError("границы корзин — по возрастанию, без повторов")
        self.name = name
        self.buckets = list(buckets)
        self.counts = [0] * (len(buckets) + 1)      # последняя — +Inf
        self.sum = 0.0
        self.count = 0

    def observe(self, v: float) -> None:
        for i, b in enumerate(self.buckets):
            if v <= b:
                self.counts[i] += 1
                break
        else:
            self.counts[-1] += 1
        self.sum += v
        self.count += 1

    def cumulative(self) -> list[int]:
        out, acc = [], 0
        for c in self.counts:
            acc += c
            out.append(acc)
        return out

    def render(self) -> str:
        cum = self.cumulative()
        les = [f"{b:g}" for b in self.buckets] + ["+Inf"]
        lines = [f'{self.name}_bucket{{le="{le}"}} {c}' for le, c in zip(les, cum, strict=True)]
        lines += [f"{self.name}_sum {self.sum:g}", f"{self.name}_count {self.count}"]
        return "\n".join(lines) + "\n"

    def quantile(self, q: float) -> float | None:
        """Как histogram_quantile в Prometheus: линейно внутри корзины."""
        if self.count == 0:
            return None
        rank = q * self.count
        cum = self.cumulative()
        for i, c in enumerate(cum):
            if c >= rank:
                if i == len(self.buckets):
                    return self.buckets[-1]
                lo = self.buckets[i - 1] if i else 0.0
                prev = cum[i - 1] if i else 0
                inside = c - prev
                return lo + (self.buckets[i] - lo) * ((rank - prev) / inside if inside else 1)
        return self.buckets[-1]
