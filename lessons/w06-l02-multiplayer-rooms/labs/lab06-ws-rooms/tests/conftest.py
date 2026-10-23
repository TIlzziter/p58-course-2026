import anyio
import pytest
from fastapi.testclient import TestClient
from starlette.testclient import WebSocketTestSession


def _receive_with_timeout(self, timeout: float = 3.0):
    """Как WebSocketTestSession.receive, но не ждёт вечно: если сервер не ответил за 3 с — TimeoutError.
    Без этого тест на недописанном коде просто зависает."""
    async def get():
        with anyio.fail_after(timeout):
            return await self._send_rx.receive()
    return self.portal.call(get)


WebSocketTestSession.receive = _receive_with_timeout


def types(out):
    """[(кому, сообщение)] → [(кому, тип)] — удобно сравнивать."""
    return [(to, msg["type"]) for to, msg in out]


@pytest.fixture
def room():
    from rooms import Room
    return Room("r1")


@pytest.fixture
def started(room):
    room.join("Аня")
    room.join("Боря")
    return room


@pytest.fixture
def client():
    import app as app_module
    app_module.rooms.clear()
    app_module.sockets.clear()
    with TestClient(app_module.app) as c:        # один event loop на все соединения теста
        yield c
