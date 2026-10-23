"""WebSocket-сервер комнат (эталон)."""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from protocol import ProtocolError, error, parse_message
from rooms import Room, RoomError

app = FastAPI()
rooms: dict[str, Room] = {}
sockets: dict[tuple[str, str], WebSocket] = {}


async def deliver(room: Room, out) -> None:
    for name, msg in out:
        ws = sockets.get((room.id, name))
        if ws is not None:
            await ws.send_json(msg)


@app.websocket("/ws/{room_id}")
async def ws_room(websocket: WebSocket, room_id: str, name: str = "", watch: bool = False):
    await websocket.accept()
    name = name.strip()
    if not name:
        await websocket.send_json(error("no_name"))
        await websocket.close(code=4400)
        return
    room = rooms.setdefault(room_id, Room(room_id))
    try:
        out = room.join(name, spectator=watch)
    except RoomError as e:
        await websocket.send_json(error(e.code))
        await websocket.close(code=4409)
        return
    sockets[(room_id, name)] = websocket
    await deliver(room, out)
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = parse_message(raw)
            except ProtocolError as e:
                await websocket.send_json(error(e.code))
                continue
            await deliver(room, room.handle(name, msg))
    except WebSocketDisconnect:
        pass
    finally:
        sockets.pop((room_id, name), None)
        await deliver(room, room.leave(name))
        if room.is_empty:
            rooms.pop(room_id, None)
