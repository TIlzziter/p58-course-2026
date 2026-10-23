"""Задачи 3–5. Движок змейки на сетке: ходы, коллизии, еда.

Правила тика — в README (таблица правил). Порядок внутри step важен.
"""
import random
from dataclasses import dataclass, field

from rng import pick

DIRS = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
OPPOSITE = {"up": "down", "down": "up", "left": "right", "right": "left"}
Cell = tuple[int, int]


@dataclass
class Snake:
    name: str
    body: list[Cell]               # голова — первая
    direction: str
    alive: bool = True
    score: int = 0

    @property
    def head(self) -> Cell:
        return self.body[0]


@dataclass
class State:
    width: int
    height: int
    snakes: dict[str, Snake]
    food: Cell | None = None
    tick: int = 0
    events: list[str] = field(default_factory=list)   # "тик:имя:причина", причины: wall self body head swap


def new_game(width: int, height: int, names: list[str], rng: random.Random) -> State:
    """Змейки длины 3: чётные по счёту смотрят вправо от левого края, нечётные — влево от правого."""
    snakes = {}
    for i, name in enumerate(names):
        y = (i + 1) * height // (len(names) + 1)
        if i % 2 == 0:
            body, d = [(2, y), (1, y), (0, y)], "right"
        else:
            body, d = [(width - 3, y), (width - 2, y), (width - 1, y)], "left"
        snakes[name] = Snake(name, body, d)
    state = State(width, height, snakes)
    state.food = place_food(state, rng)
    return state


def turn(current: str, wanted: str | None) -> str:
    return wanted or current


def next_head(snake: Snake) -> Cell:
    dx, dy = DIRS[snake.direction]
    return snake.head[0] + dx, snake.head[1] + dy


def place_food(state: State, rng: random.Random) -> Cell | None:
    """Случайная клетка, не занятая живыми змейками (через pick). Свободных нет → None."""
    return pick({(x, y) for x in range(state.width) for y in range(state.height)}, rng)


def step(state: State, inputs: dict[str, str], rng: random.Random) -> State:
    for s in state.snakes.values():
        if not s.alive:
            continue
        s.direction = turn(s.direction, inputs.get(s.name))
        s.body = [next_head(s)] + s.body[:-1]
        # TODO задача 4: стены, своё тело, чужое тело, лоб в лоб, обмен клетками
        if s.head == state.food:
            s.score += 1        # TODO задача 5: рост и новая еда
    state.tick += 1
    return state
