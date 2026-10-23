"""API крестиков-ноликов. Каркас сгенерировал агент — сверьте его со SPEC.md и доделайте."""
from fastapi import FastAPI, HTTPException

from . import game
from .schemas import JoinIn, MoveIn, RoomCreate

app = FastAPI(title="Крестики-нолики P58")
rooms: dict[int, dict] = {}
MARKS = ("X", "O")


def error(status: int, code: str, message: str) -> HTTPException:
    """Ошибка в формате спеки: {"detail": {"code": ..., "message": ...}}."""
    return HTTPException(status, detail={"code": code, "message": message})


# TODO (задача 7*): ошибки валидации FastAPI (422) тоже должны быть в формате спеки.


def public(room_id: int) -> dict:
    r = rooms[room_id]
    return {"room_id": room_id, "players": r["players"], "board": r["board"], "turn": r["turn"],
            "status": r["status"], "winner": r["winner"]}


@app.get("/health")
def health() -> dict:
    return {"status": "running"}


@app.post("/rooms")
def create_room(body: RoomCreate) -> dict:
    room_id = len(rooms)
    rooms[room_id] = {"players": [body.player], "board": "." * 9, "turn": None, "status": "waiting", "winner": None}
    return public(room_id)


@app.get("/rooms")
def list_rooms() -> list[dict]:
    return []   # TODO (задача 6)


@app.get("/rooms/{room_id}")
def get_room(room_id: int) -> dict:
    return public(room_id)


@app.post("/rooms/{room_id}/join")
def join(room_id: int, body: JoinIn) -> dict:
    raise NotImplementedError("задача 3")


@app.post("/rooms/{room_id}/moves")
def move(room_id: int, body: MoveIn) -> dict:
    r = rooms[room_id]
    mark = MARKS[r["players"].index(body.player)]
    r["board"] = game.place(r["board"], body.cell, mark)
    # TODO (задачи 4 и 5): проверки из спеки, смена хода, победа и ничья
    return public(room_id)
