"""Контест 14 · E5*: подбор соперников с расширяющимся окном."""


def window(wait: float, base: int = 100, step: int = 50, every: float = 10) -> int:
    """Допустимая разница рейтингов после ожидания wait секунд: base + step · ⌊wait / every⌋."""
    return base + step * int(wait // every)


def matchmake(events: list[tuple[float, str, int]], horizon: float, tick: float = 1.0, **kw) -> list[tuple]:
    """События (время, игрок, рейтинг) по времени — игрок встаёт в очередь. Каждые tick секунд от 0 до
    horizon включительно (сначала добавляем пришедших к этому моменту): перебираем ожидающих по времени
    прихода (затем по имени); для каждого свободного ищем свободного соперника с |Δ| ≤ min(окно обоих),
    из подходящих — с наименьшей |Δ|, затем пришедшего раньше, затем по имени. Ответ — пары
    (момент, первый, второй, |Δ|) в порядке создания."""
    queue: list[tuple[float, str, int]] = []
    out = []
    i = 0
    steps = int(round(horizon / tick))
    for s in range(steps + 1):
        t = s * tick
        while i < len(events) and events[i][0] <= t + 1e-9:
            queue.append(events[i])
            i += 1
        queue.sort(key=lambda e: (e[0], e[1]))
        taken: set[str] = set()
        for a in queue:
            if a[1] in taken:
                continue
            best = None
            for b in queue:
                if b[1] == a[1] or b[1] in taken:
                    continue
                d = abs(a[2] - b[2])
                if d <= min(window(t - a[0], **kw), window(t - b[0], **kw)):
                    k = (d, b[0], b[1])
                    if best is None or k < best[0]:
                        best = (k, b)
            if best:
                b = best[1]
                taken |= {a[1], b[1]}
                out.append((t, a[1], b[1], best[0][0]))
        queue = [e for e in queue if e[1] not in taken]
    return out
