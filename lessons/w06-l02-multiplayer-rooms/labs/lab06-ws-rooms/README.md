# Лабораторная 06. Комнаты на WebSocket

Делаем мультиплеер «4 в ряд»: два игрока в одной комнате, сервер — **источник истины**. Клиент присылает только
намерение («хочу в столбец 3»), сервер проверяет очередь и правила и рассылает новое состояние **обоим**.

Код разделён на три слоя, как на лекции:

| Файл | Что делает | Знает про WebSocket? |
|---|---|---|
| `connect4.py` | правила игры (готово, из лабы 04) | нет |
| `protocol.py` | разбор и проверка сообщений клиента | нет |
| `rooms.py` | комната: игроки, очередь, кому что отправить | нет |
| `app.py` | WebSocket-эндпоинт FastAPI: принять, разобрать, отдать комнате, разослать | да |

Комната возвращает **исходящие** — список пар `(кому, сообщение)`. Поэтому её можно тестировать без сети,
а `app.py` остаётся тонким.

```bash
pip install -r ../../../../requirements.txt     # один раз, из корня курса
python check.py
python check.py -v 3
```

## Протокол

| Направление | Сообщение | Когда |
|---|---|---|
| → сервер | `{"type": "move", "col": 0..6}` | ход |
| → сервер | `{"type": "chat", "text": "..."}` | чат, 1–200 символов |
| → сервер | `{"type": "ping"}` | проверка связи |
| ← клиенту | `{"type": "welcome", "room": "r1", "color": 1}` | после входа (у зрителя `color: 0` и `state`) |
| ← всем | `{"type": "start", "players": {"1": "Аня", "2": "Боря"}, "state": {...}}` | вошёл второй игрок |
| ← всем | `{"type": "state", "state": {...}, "last": {"col": 3, "by": 1}}` | после хода |
| ← всем | `{"type": "game_over", "result": "win1"}` | победа или ничья (`"draw"`) |
| ← всем | `{"type": "opponent_left", "name": "Аня"}` | игрок вышел; во время партии — ещё `game_over` с `"reason": "forfeit"` |
| ← клиенту | `{"type": "error", "code": "..."}` | ошибка; соединение **не закрываем** |

Коды ошибок: `bad_json`, `bad_type`, `bad_field` (протокол), `not_started`, `not_your_turn`, `column_full`,
`bad_column`, `game_over`, `spectator` (комната), `room_full`, `name_taken`, `no_name` (вход — после ошибки
соединение закрываем).

## Задачи

| № | Где | Что сделать |
|---|---|---|
| 1 | `parse_message` | Невалидный JSON → `bad_json`; не объект, нет или неизвестный `type` → `bad_type`; не тот набор ключей, `col` не `int` (а `true` — это `bool`, тоже нет!) или вне 0..6, пустой/длинный текст → `bad_field`. Текст чата обрезать `strip()`. |
| 2 | `Room.join` | Цвета 1 и 2; повтор имени → `RoomError("name_taken")`; третий игрок или игра уже началась → `room_full`. Когда вошёл второй — `start` всем (сначала `welcome` второму). |
| 3 | `Room.handle` (ход) | `not_started`, `not_your_turn`, ошибки `MoveError` (`e.code`), `game_over` — только отправителю. Удачный ход — `state` всем; конец партии — затем `game_over` всем. |
| 4 | `Room.handle` (чат, ping) | `pong` только отправителю, `chat` — всем с полем `from`. Работают и до начала партии. |
| 5 | `Room.leave` | Оставшимся `opponent_left`; если партия шла — ещё `game_over` с победой оставшегося и `"reason": "forfeit"`. Вышедшему ничего не шлём. |
| 6 | `app.py` | Нет имени → `no_name` и закрыть; `RoomError` → ошибка и закрыть; `ProtocolError` → ошибка, **продолжать**; отключение (`WebSocketDisconnect`) → `leave` и разослать; пустую комнату удалить из `rooms`. |
| 7* | зрители | `join(name, spectator=True)` (в URL `&watch=true`): `welcome` с `color: 0` и текущим `state`; получают все рассылки после игроков; ход зрителя → `spectator`; чат можно. |

Подсказки:
* Задача 1: `type(col) is int` отсекает `True`, а `isinstance(True, int)` — истина.
* Задача 6: `try: ... except WebSocketDisconnect: ... finally:` — уборка в `finally` сработает при любом выходе.
* Тесты WebSocket используют `with TestClient(app) as client:` — так все соединения теста живут в одном event loop
  и могут слать сообщения друг другу.

## Проверка у экрана

Запустите `uvicorn app:app --reload` и откройте два окна браузера с консолью:

```js
const ws = new WebSocket("ws://localhost:8000/ws/test?name=Аня");
ws.onmessage = (e) => console.log(JSON.parse(e.data));
ws.send(JSON.stringify({type: "move", col: 3}));
```
