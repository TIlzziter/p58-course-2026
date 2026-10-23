"""Задача 1. Честный рандом: Фишер–Йетс и выбор свободной клетки."""
import random


def shuffle(items: list, rng: random.Random) -> list:
    """Новый перемешанный список; все n! перестановок равновероятны. Исходный не меняем."""
    a = items
    for i in range(len(a)):
        j = rng.randrange(len(a))
        a[i], a[j] = a[j], a[i]
    return a


def pick(cells, rng: random.Random):
    """Случайная клетка из множества. Результат должен зависеть только от seed и содержимого cells. Пусто → None."""
    return rng.choice(list(cells))
