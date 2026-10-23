"""Задача 7*. Rate limit и проверка счёта в FastAPI."""
import math  # noqa: F401
import time
from collections.abc import Callable

from fastapi import FastAPI, Request  # noqa: F401
from fastapi.responses import JSONResponse  # noqa: F401
from pydantic import BaseModel, Field  # noqa: F401
from ratelimit import KeyedLimiter

MAX_SCORE = 10_000


class Score(BaseModel):
    score: int  # TODO: границы 0..MAX_SCORE


def create_app(limit: int = 5, window: float = 60, now: Callable[[], float] = time.monotonic) -> FastAPI:
    """Приложение с двумя маршрутами:
      GET  /health     — {"status": "ok"}, без ограничений;
      POST /api/score  — {"score": int от 0 до MAX_SCORE} (иначе 422), ответ {"saved": score}.
    Все пути, начинающиеся с /api/, ограничены KeyedLimiter(limit, window, now) по ключу: заголовок
    X-User-Id, а без него — IP клиента. Отказ — 429, тело {"error": "rate_limited"},
    заголовок Retry-After — целое число секунд, округлённое вверх (не меньше 1).
    """
    app = FastAPI()
    limiter = KeyedLimiter(limit, window, now)  # noqa: F841

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.post("/api/score")
    async def save_score(body: Score):
        return {"saved": body.score}

    return app
