"""Задачи 3–4. Метрики RED и гистограмма."""


def percentile(values, q):
    """Метод ближайшего ранга: элемент с индексом ceil(q·n) − 1 в отсортированном списке."""
    s = sorted(values)
    return s[int(q * len(s))]


def red(records: list[dict], start: float, end: float) -> dict | None:
    """Rate (запросов в секунду), Errors (доля 5xx), p50 и p95 длительности ms по запросам с ts в [start, end).
    Пусто — None."""
    win = [r for r in records if start <= r["ts"] <= end]
    ms = [r["ms"] for r in win]
    return {
        "rate": len(win) / (end - start),
        "errors": sum(r["status"] >= 400 for r in win) / len(win),
        "p50": percentile(ms, 0.5),
        "p95": percentile(ms, 0.95),
    }


class Histogram:
    """Гистограмма в стиле Prometheus: значение v попадает в первую корзину с v <= le.
    Границы — непустой список по возрастанию без повторов, иначе ValueError."""

    def __init__(self, name: str, buckets: list[float]):
        self.name = name
        self.buckets = list(buckets)
        self.counts = [0] * (len(buckets) + 1)      # последняя — +Inf
        self.sum = 0.0
        self.count = 0

    def observe(self, v: float) -> None:
        for i, b in enumerate(self.buckets):
            if v < b:
                self.counts[i] += 1
                break
        self.sum += v
        self.count += 1

    def render(self) -> str:
        """Текстовый формат Prometheus: накопленные bucket, затем _sum и _count. Числа — через :g."""
        lines = [f'{self.name}_bucket{{le="{b:g}"}} {c}' for b, c in zip(self.buckets, self.counts, strict=False)]
        lines += [f"{self.name}_sum {self.sum:g}", f"{self.name}_count {self.count}"]
        return "\n".join(lines) + "\n"

    def quantile(self, q: float) -> float | None:
        """Как histogram_quantile в Prometheus. Пусто — None."""
        raise NotImplementedError
