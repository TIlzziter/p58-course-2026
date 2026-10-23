"""API крестиков-ноликов по SPEC.md (эталон)."""
from fastapi import FastAPI, HTTPException, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from . import game
from .schemas import JoinIn, MoveIn, RoomCreate

app = FastAPI(title="Крестики-нолики P58")
rooms: dict[int, dict] = {}
MARKS = ("X", "O")


def error(status: int, code: str, message: str) -> HTTPException:
    return HTTPException(status, detail={"code": code, "message": message})


@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):  # noqa: ARG001
    return JSONResponse(status_code=422, content={"detail": {"code": "validation_error", "message": "Неверные данные запроса"}})


def public(room_id: int) -> dict:
    r = rooms[room_id]
    return {"room_id": room_id, "players": r["players"], "board": r["board"], "turn": r["turn"],
            "status": r["status"], "winner": r["winner"]}


def get_or_404(room_id: int) -> dict:
    if room_id not in rooms:
        raise error(404, "room_not_found", f"Комнаты {room_id} нет")
    return rooms[room_id]


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/rooms", status_code=201)
def create_room(body: RoomCreate) -> dict:
    room_id = max(rooms, default=0) + 1
    rooms[room_id] = {"players": [body.player], "board": "." * 9, "turn": None, "status": "waiting", "winner": None}
    return public(room_id)


@app.get("/rooms")
def list_rooms(status: str | None = Query(default=None, pattern="^(waiting|playing|finished)$")) -> list[dict]:
    return [public(i) for i in sorted(rooms) if status is None or rooms[i]["status"] == status]


@app.get("/rooms/{room_id}")
def get_room(room_id: int) -> dict:
    get_or_404(room_id)
    return public(room_id)


@app.post("/rooms/{room_id}/join")
def join(room_id: int, body: JoinIn) -> dict:
    r = get_or_404(room_id)
    if len(r["players"]) >= 2:
        raise error(409, "room_full", "Комната заполнена")
    if body.player in r["players"]:
        raise error(409, "name_taken", "Это имя уже в комнате")
    r["players"].append(body.player)
    r["status"] = "playing"
    r["turn"] = r["players"][0]
    return public(room_id)


@app.post("/rooms/{room_id}/moves")
def move(room_id: int, body: MoveIn) -> dict:
    r = get_or_404(room_id)
    if body.player not in r["players"]:
        raise error(403, "not_a_player", "Вы не играете в этой комнате")
    if r["status"] != "playing":
        raise error(409, "not_playing", "Партия не идёт")
    if body.player != r["turn"]:
        raise error(409, "not_your_turn", f"Сейчас ходит {r['turn']}")
    mark = MARKS[r["players"].index(body.player)]
    try:
        r["board"] = game.place(r["board"], body.cell, mark)
    except ValueError:
        raise error(409, "cell_taken", "Клетка занята") from None
    w = game.winner(r["board"])
    if w is not None:
        r["status"], r["winner"], r["turn"] = "finished", r["players"][MARKS.index(w)], None
    elif game.is_draw(r["board"]):
        r["status"], r["turn"] = "finished", None
    else:
        r["turn"] = r["players"][1 - r["players"].index(body.player)]
    return public(room_id)
