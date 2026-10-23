"""Контест 2 — E1 и E5*: FastAPI (эталон)."""
import hashlib
import hmac
import json
import os
import time
from urllib.parse import parse_qsl

from fastapi import FastAPI, HTTPException
from minesweeper import GameOver, Minesweeper
from pydantic import BaseModel, Field

app = FastAPI()


# ---------- E1 ----------
class CheckIn(BaseModel):
    init_data: str


def check_init_data(raw: str, token: str, now: int, max_age: int = 86400) -> int | None:
    try:
        fields = dict(parse_qsl(raw, strict_parsing=True))
    except ValueError:
        return None
    received = fields.pop("hash", "")
    dcs = "\n".join(f"{k}={v}" for k, v in sorted(fields.items()))
    secret = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    if not hmac.compare_digest(received, hmac.new(secret, dcs.encode(), hashlib.sha256).hexdigest()):
        return None
    if not 0 <= now - int(fields.get("auth_date", "0")) <= max_age:
        return None
    try:
        return int(json.loads(fields["user"])["id"])
    except (KeyError, ValueError, TypeError):
        return None


@app.post("/check")
def check(body: CheckIn) -> dict:
    user_id = check_init_data(body.init_data, os.environ["BOT_TOKEN"], int(time.time()))
    return {"ok": user_id is not None, "user_id": user_id}


# ---------- E5* ----------
class NewGame(BaseModel):
    rows: int = Field(ge=2, le=30)
    cols: int = Field(ge=2, le=30)
    mines: list[tuple[int, int]]


class Cell(BaseModel):
    r: int
    c: int


games: dict[int, Minesweeper] = {}


def state(gid: int) -> dict:
    g = games[gid]
    return {"id": gid, "view": g.view(), "status": g.status, "mines_left": g.mines_left()}


def get(gid: int) -> Minesweeper:
    if gid not in games:
        raise HTTPException(404, "Нет игры")
    return games[gid]


@app.post("/games", status_code=201)
def new_game(body: NewGame) -> dict:
    mines = set(body.mines)
    if any(not (0 <= r < body.rows and 0 <= c < body.cols) for r, c in mines) or len(mines) >= body.rows * body.cols:
        raise HTTPException(422, "Мины вне поля или их слишком много")
    gid = len(games) + 1
    games[gid] = Minesweeper(body.rows, body.cols, mines)
    return state(gid)


@app.post("/games/{gid}/open")
def open_cell(gid: int, cell: Cell) -> dict:
    g = get(gid)
    if not (0 <= cell.r < g.rows and 0 <= cell.c < g.cols):
        raise HTTPException(422, "Клетка вне поля")
    try:
        g.open(cell.r, cell.c)
    except GameOver:
        raise HTTPException(409, "Игра окончена") from None
    return state(gid)


@app.post("/games/{gid}/flag")
def flag_cell(gid: int, cell: Cell) -> dict:
    g = get(gid)
    try:
        g.flag(cell.r, cell.c)
    except GameOver:
        raise HTTPException(409, "Игра окончена") from None
    return state(gid)
