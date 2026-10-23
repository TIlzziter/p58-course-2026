"""Контест 3, D1–D3: WebSocket-эндпоинты (эталон)."""
import json
from collections import defaultdict, deque

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()


# D1
@app.websocket("/ws/echo")
async def echo(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            raw = await ws.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await ws.send_json({"type": "error", "code": "bad_json"})
                continue
            await ws.send_json({"type": "echo", "data": data})
    except WebSocketDisconnect:
        pass


# D2
counter = {"value": 0}
counter_clients: set[WebSocket] = set()


@app.websocket("/ws/counter")
async def count(ws: WebSocket):
    await ws.accept()
    counter_clients.add(ws)
    await ws.send_json({"type": "count", "value": counter["value"]})
    try:
        while True:
            msg = await ws.receive_json()
            if msg.get("type") == "inc":
                counter["value"] += 1
                for c in list(counter_clients):
                    await c.send_json({"type": "count", "value": counter["value"]})
    except WebSocketDisconnect:
        pass
    finally:
        counter_clients.discard(ws)


# D3
HISTORY = 5
history: dict[str, deque] = defaultdict(lambda: deque(maxlen=HISTORY))
chat_clients: dict[str, set[WebSocket]] = defaultdict(set)


@app.websocket("/ws/chat/{room}")
async def chat(ws: WebSocket, room: str, name: str):
    await ws.accept()
    await ws.send_json({"type": "history", "messages": list(history[room])})
    chat_clients[room].add(ws)
    try:
        while True:
            text = (await ws.receive_text()).strip()
            if not text:
                continue
            msg = {"from": name, "text": text}
            history[room].append(msg)
            for c in list(chat_clients[room]):
                await c.send_json({"type": "chat", **msg})
    except WebSocketDisconnect:
        pass
    finally:
        chat_clients[room].discard(ws)
