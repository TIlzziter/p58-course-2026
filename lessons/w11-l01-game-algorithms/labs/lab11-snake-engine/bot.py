"""Задача 7*. Бот: кратчайший путь к еде (BFS), иначе — любой безопасный ход."""
from engine import State


def ai_move(state: State, name: str) -> str:
    return state.snakes[name].direction
