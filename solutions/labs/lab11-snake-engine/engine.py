"""Задачи 3–5. Движок змейки на сетке: ходы, коллизии, еда."""
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
    events: list[str] = field(default_factory=list)


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


# ---------- 3. Поворот и движение ----------


def turn(current: str, wanted: str | None) -> str:
    if wanted is None:
        return current
    if wanted not in DIRS:
        raise ValueError(wanted)
    return current if OPPOSITE[wanted] == current else wanted


def next_head(snake: Snake) -> Cell:
    dx, dy = DIRS[snake.direction]
    return snake.head[0] + dx, snake.head[1] + dy


# ---------- 5. Еда ----------


def place_food(state: State, rng: random.Random) -> Cell | None:
    busy = {c for s in state.snakes.values() if s.alive for c in s.body}
    free = {(x, y) for x in range(state.width) for y in range(state.height)} - busy
    return pick(free, rng)


# ---------- 3–5. Тик ----------


def step(state: State, inputs: dict[str, str], rng: random.Random) -> State:
    alive = [s for s in state.snakes.values() if s.alive]
    old_heads = {s.name: s.head for s in alive}
    for s in alive:
        s.direction = turn(s.direction, inputs.get(s.name))
    heads = {s.name: next_head(s) for s in alive}
    eats = {s.name for s in alive if heads[s.name] == state.food}
    new_bodies = {s.name: [heads[s.name]] + (s.body if s.name in eats else s.body[:-1]) for s in alive}

    dead: set[str] = set()
    for s in alive:
        x, y = h = heads[s.name]
        if not (0 <= x < state.width and 0 <= y < state.height):
            dead.add(s.name)
            state.events.append(f"{state.tick + 1}:{s.name}:wall")
            continue
        for o in alive:
            if o.name != s.name and heads[o.name] == h:
                dead.add(s.name)
                state.events.append(f"{state.tick + 1}:{s.name}:head")
                break
            if o.name != s.name and heads[o.name] == old_heads[s.name] and h == old_heads[o.name]:
                dead.add(s.name)
                state.events.append(f"{state.tick + 1}:{s.name}:swap")
                break
            if h in new_bodies[o.name][1:]:
                dead.add(s.name)
                state.events.append(f"{state.tick + 1}:{s.name}:{'self' if o is s else 'body'}")
                break

    for s in alive:
        if s.name in dead:
            s.alive = False
        else:
            s.body = new_bodies[s.name]
    eaten = False
    for name in eats - dead:
        state.snakes[name].score += 1
        eaten = True
    state.tick += 1
    if eaten:
        state.food = place_food(state, rng)
    return state
