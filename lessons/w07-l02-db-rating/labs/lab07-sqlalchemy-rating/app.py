"""HTTP API рейтинга (задача 8*)."""
import os
from typing import Literal

import repo  # noqa: F401
from db import make_engine
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

engine = make_engine(os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///rating.db"))
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
app = FastAPI(title="Рейтинг")


async def get_session():
    async with SessionLocal() as session:
        yield session


class PlayerIn(BaseModel):
    tg_id: int
    name: str = Field(min_length=1, max_length=64)


class MatchIn(BaseModel):
    game: str = Field(min_length=1, max_length=32)
    player1: PlayerIn
    player2: PlayerIn
    result: Literal["win1", "win2", "draw"]


@app.post("/matches", status_code=201)
async def post_match(body: MatchIn, session: AsyncSession = Depends(get_session)):
    # TODO: 400 "same_player"; в ОДНОЙ транзакции создать игроков и записать матч
    raise HTTPException(501, "not_implemented")


@app.get("/leaderboard")
async def get_leaderboard(limit: int = 10, session: AsyncSession = Depends(get_session)):
    raise HTTPException(501, "not_implemented")


@app.get("/players/{tg_id}/history")
async def get_history(tg_id: int, limit: int = 5, session: AsyncSession = Depends(get_session)):
    raise HTTPException(501, "not_implemented")
