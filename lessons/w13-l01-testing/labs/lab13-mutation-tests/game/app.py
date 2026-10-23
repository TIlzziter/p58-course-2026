"""Чат комнаты по WebSocket."""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

MAX_TEXT = 200


def create_app() -> FastAPI:
    app = FastAPI()
    rooms: dict[str, dict[str, WebSocket]] = {}

    async def broadcast(code: str, message: dict) -> None:
        for ws in list(rooms.get(code, {}).values()):
            await ws.send_json(message)

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.websocket("/ws/{code}")
    async def room_ws(ws: WebSocket, code: str):
        """Первое сообщение — {"type": "hello", "name": "..."}, иначе закрываем с кодом 4001.
        Имя уже занято в комнате — закрываем с кодом 4009.
        Дальше: {"type": "chat", "text": "..."} — пробелы по краям убираем, пустое игнорируем,
        длиннее MAX_TEXT — только отправителю {"type": "error", "reason": "too_long"}.
        Всем в комнате: joined / chat / left."""
        await ws.accept()
        hello = await ws.receive_json()
        name = str(hello.get("name", "")).strip() if hello.get("type") == "hello" else ""
        if not name:
            await ws.close(code=4001)
            return
        room = rooms.setdefault(code, {})
        if name in room:
            await ws.close(code=4009)
            return
        room[name] = ws
        await broadcast(code, {"type": "joined", "name": name, "players": sorted(room)})
        try:
            while True:
                msg = await ws.receive_json()
                if msg.get("type") != "chat":
                    continue
                text = str(msg.get("text", "")).strip()
                if not text:
                    continue
                if len(text) > MAX_TEXT:
                    await ws.send_json({"type": "error", "reason": "too_long"})
                    continue
                await broadcast(code, {"type": "chat", "from": name, "text": text})
        except WebSocketDisconnect:
            del room[name]
            await broadcast(code, {"type": "left", "name": name, "players": sorted(room)})

    return app
