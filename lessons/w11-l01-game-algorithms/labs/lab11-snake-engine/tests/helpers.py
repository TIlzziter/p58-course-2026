import random

from engine import Snake, State


def board(w, h, food=None, **snakes):
    """board(6, 4, food=(5, 0), a=([(2, 1), (1, 1), (0, 1)], "right"))"""
    return State(w, h, {n: Snake(n, list(body), d) for n, (body, d) in snakes.items()}, food)


def rng(seed=1):
    return random.Random(seed)
