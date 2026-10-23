import random

import pytest
from games import ConnectFour, TicTacToe
from search import Stats


@pytest.fixture
def ttt():
    return TicTacToe()


@pytest.fixture
def c4():
    return ConnectFour()


@pytest.fixture
def small():
    return ConnectFour(4, 4, 3)


def random_positions(game, n, seed, max_moves=6, min_moves=0):
    rng = random.Random(seed)
    out = []
    while len(out) < n:
        s = game.initial()
        for _ in range(rng.randint(min_moves, max_moves)):
            ms = game.moves(s)
            if not ms:
                break
            s = game.play(s, rng.choice(ms))
        if game.winner(s) is None:
            out.append(s)
    return out


class Budget(Stats):
    """Stats с пределом: без отсечений поиск на «Четырёх в ряд» не закончится до ночи — падаем сразу."""

    limit = 100_000

    def __setattr__(self, key, value):
        if key == "nodes" and value > self.limit:
            raise AssertionError(f"больше {self.limit} узлов — отсечения работают?")
        super().__setattr__(key, value)
