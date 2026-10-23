# Лабораторная 13. Тесты, которые ловят баги

Обычно код пишете вы, а тесты дают. Здесь наоборот: код в `game/` **правильный**, а тесты пишете вы — в
`mytests/`. Как понять, что тесты хорошие? Мы портим код маленькими правками («мутантами»): `<` на `<=`, `+ 2` на
`+ 1`, забытая строка. Хороший набор тестов падает на каждом мутанте — «убивает» его. Покрытие строк этого не
показывает: строка может выполняться, а её результат никто не проверяет.

```bash
python check.py           # все задачи
python report.py rooms    # кто из мутантов rooms выжил
python -m pytest mytests  # просто запустить свои тесты
```

| № | Код | Ваши тесты | Что потренировать |
|---|---|---|---|
| 1 | `game/scoring.py` — очки, бонус серии, Эло | `mytests/test_scoring.py` | `parametrize`, границы, `pytest.raises` |
| 2 | `game/rooms.py` — комната лобби | `mytests/test_rooms.py` | фикстуры, состояние после действий |
| 3 | `game/matchmaker.py` — подбор пары (asyncio) | `mytests/test_matchmaker.py` | async-тесты, таймауты, `create_task` |
| 4 | `game/app.py` — чат комнаты по WebSocket | `mytests/test_app.py` | `TestClient`, `websocket_connect`, коды закрытия |
| 5 | `game/repo.py` — история партий (SQLAlchemy) | `mytests/test_repo.py` | тестовая БД `sqlite://`, фикстура с данными |
| 6* | `mutate.py` — свой мутатор на `ast` | — | `ast.walk`, `ast.unparse` |

Задача 1–5 засчитывается, когда ваши тесты **проходят** на правильном коде и **падают** на каждом мутанте из
`tests/mutants.py`. Список мутантов открыт, но честнее сначала написать тесты по docstring и только потом смотреть,
кто выжил.

## Правила

* `game/` не меняйте: мутанты накладываются на этот код как замена строки.
* Тест не должен зависать. WebSocket-тест, который ждёт сообщение, которого нет, висит вечно. Сначала читайте у
  того, кто точно получит ответ (у отправителя), и посылайте «маячок», если ждёте событие у другого клиента.
* Не проверяйте детали, которых нет в docstring (например, точный текст исключения).
* Async-тесты пишутся как `async def test_...` — `asyncio_mode = auto` уже включён в `pytest.ini`.

## Подсказки

* Тест на `TestClient` с WebSocket:

```python
with TestClient(create_app()) as client:
    with client.websocket_connect("/ws/R1") as ws:
        ws.send_json({"type": "hello", "name": "ann"})
        assert ws.receive_json()["type"] == "joined"
```

* Закрытие сервером: `with pytest.raises(WebSocketDisconnect) as e: ws.receive_json()`, код — `e.value.code`.
* Тестовая БД: `create_engine("sqlite://")` — база в памяти, новая для каждого теста, `Base.metadata.create_all`.
* Матчмейкер: `asyncio.create_task(mm.find("ann"))`, затем `await asyncio.sleep(0)`, чтобы задача встала в очередь.
* Задача 6*: порядок и формат описаний — в docstring `mutate.py`. Готовые инструменты — `mutmut`, `cosmic-ray`;
  здесь пишем свой, чтобы понять идею.
