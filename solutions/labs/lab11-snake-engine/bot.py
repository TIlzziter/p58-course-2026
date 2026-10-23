"""Задача 7*. Бот: кратчайший путь к еде (BFS), иначе — любой безопасный ход."""
from collections import deque

from engine import DIRS, OPPOSITE, State


def _blocked(state: State, me: str) -> set:
    cells = set()
    for s in state.snakes.values():
        if s.alive:
            cells |= set(s.body[:-1])     # хвосты к следующему тику уйдут (если никто не ест)
    return cells


def _inside(state: State, c) -> bool:
    return 0 <= c[0] < state.width and 0 <= c[1] < state.height


def ai_move(state: State, name: str) -> str:
    snake = state.snakes[name]
    blocked = _blocked(state, name)
    order = [d for d in ("up", "right", "down", "left") if d != OPPOSITE[snake.direction]]
    first = {}
    q = deque()
    for d in order:
        dx, dy = DIRS[d]
        c = (snake.head[0] + dx, snake.head[1] + dy)
        if _inside(state, c) and c not in blocked and c not in first:
            first[c] = d
            q.append(c)
    seen = set(first)
    while q:
        c = q.popleft()
        if c == state.food:
            return first[c]
        for dx, dy in DIRS.values():
            n = (c[0] + dx, c[1] + dy)
            if _inside(state, n) and n not in blocked and n not in seen:
                seen.add(n)
                first[n] = first[c]
                q.append(n)
    for d in order:                       # еда недостижима — любой безопасный ход
        dx, dy = DIRS[d]
        c = (snake.head[0] + dx, snake.head[1] + dy)
        if _inside(state, c) and c not in blocked:
            return d
    return snake.direction
