"""WebSocket-сервер комнат: /ws/{room_id}?name=Аня[&watch=true]. Задача 6."""
from fastapi import FastAPI, WebSocket
from protocol import parse_message
from rooms import Room

app = FastAPI()
rooms: dict[str, Room] = {}
sockets: dict[tuple[str, str], WebSocket] = {}    # (комната, имя) → соединение


async def deliver(room: Room, out) -> None:
    """Разослать исходящие сообщения комнаты по соединениям."""
    for name, msg in out:
        ws = sockets.get((room.id, name))
        if ws is not None:
            await ws.send_json(msg)


@app.websocket("/ws/{room_id}")
async def ws_room(websocket: WebSocket, room_id: str, name: str = "", watch: bool = False):
    await websocket.accept()
    room = rooms.setdefault(room_id, Room(room_id))
    out = room.join(name, spectator=watch)
    sockets[(room_id, name)] = websocket
    await deliver(room, out)
    while True:
        msg = parse_message(await websocket.receive_text())
        await deliver(room, room.handle(name, msg))
