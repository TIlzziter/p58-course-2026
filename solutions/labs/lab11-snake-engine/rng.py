"""Задача 1. Честный рандом: Фишер–Йетс и выбор свободной клетки."""
import random


def shuffle(items: list, rng: random.Random) -> list:
    """Новый перемешанный список; все n! перестановок равновероятны. Исходный не меняем."""
    a = list(items)
    for i in range(len(a) - 1, 0, -1):
        j = rng.randrange(i + 1)          # 0 ≤ j ≤ i, а не randrange(len(a))
        a[i], a[j] = a[j], a[i]
    return a


def pick(cells, rng: random.Random):
    """Случайная клетка из множества: сортируем, чтобы результат зависел только от seed. Пусто → None."""
    cells = sorted(cells)
    if not cells:
        return None
    return cells[rng.randrange(len(cells))]
