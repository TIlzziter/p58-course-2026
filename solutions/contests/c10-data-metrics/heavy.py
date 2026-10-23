"""Контест 10 · E5*: частые элементы потока в памяти O(k)."""


def misra_gries(stream, k: int) -> dict:
    """Алгоритм Мисры — Гриса с k−1 счётчиками: элемент есть — +1; есть место — новый счётчик 1;
    иначе — все счётчики −1, нулевые удалить (новый элемент не добавляется). Ответ — счётчики,
    отсортированные по убыванию значения, при равенстве — по ключу."""
    counters: dict = {}
    for x in stream:
        if x in counters:
            counters[x] += 1
        elif len(counters) < k - 1:
            counters[x] = 1
        else:
            for key in list(counters):
                counters[key] -= 1
                if counters[key] == 0:
                    del counters[key]
    return dict(sorted(counters.items(), key=lambda kv: (-kv[1], kv[0])))


def heavy_hitters(stream, k: int) -> list:
    """Второй проход: из кандидатов Мисры — Гриса оставить тех, кто встречается больше n/k раз (по возрастанию)."""
    items = list(stream)
    cand = misra_gries(items, k)
    n = len(items)
    return sorted(x for x in cand if items.count(x) * k > n)
