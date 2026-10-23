"""HTTP API рейтинга (задача 8*)."""
import os
from typing import Literal

import repo
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
    if body.player1.tg_id == body.player2.tg_id:
        raise HTTPException(400, "same_player")
    async with session.begin():               # всё или ничего: игроки, матч, рейтинги
        for p in (body.player1, body.player2):
            await repo.get_or_create_player(session, p.tg_id, p.name)
        match = await repo.record_match(session, body.game, body.player1.tg_id, body.player2.tg_id, body.result)
    return {"id": match.id, "delta1": match.delta1, "delta2": match.delta2}


@app.get("/leaderboard")
async def get_leaderboard(limit: int = 10, session: AsyncSession = Depends(get_session)):
    rows = await repo.leaderboard(session, min(max(limit, 1), 100))
    return [{"name": n, "rating": r, "games": g} for n, r, g in rows]


@app.get("/players/{tg_id}/history")
async def get_history(tg_id: int, limit: int = 5, session: AsyncSession = Depends(get_session)):
    try:
        return await repo.history(session, tg_id, min(max(limit, 1), 50))
    except LookupError:
        raise HTTPException(404, "no_player") from None
