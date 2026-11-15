# Лабораторная 08. Матчмейкинг на Redis

Пока комнаты и очередь живут в памяти процесса, сервер можно запустить только в **одной** копии: вторая копия
просто не знает, что творится в первой. Поэтому переносим всё «горячее» в Redis: сессии, ограничение частоты,
очередь поиска соперника, комнаты и события между копиями.

| Файл | Задачи | Тип данных Redis |
|---|---|---|
| `sessions.py` | 1 сессии, 2 rate limit | string + TTL, `INCR` |
| `matchmaking.py` | 3 очередь, 4 поиск пары | sorted set (score = рейтинг) |
| `rooms.py` | 5 комнаты и ссылка-приглашение, 6 pub/sub | hash + TTL, каналы |
| `cache.py` | 7* кэш таблицы лидеров | string + TTL |

Тесты работают на `fakeredis` — это Redis в памяти с тем же API, что у `redis.asyncio`. Настоящий Redis не нужен,
но если хочется потрогать живой — `docker run -p 6379:6379 redis:8` и `Redis.from_url("redis://localhost", decode_responses=True)`.

```bash
python check.py           # все задачи
python check.py -v 4      # подробности по задаче 4
```

## Ключи

| Ключ | Тип | Значение | TTL |
|---|---|---|---|
| `session:<token>` | string | id пользователя | 1 ч, продлевается при каждом обращении |
| `rl:<key>` | string | счётчик запросов | окно `window`, ставится **только** первым запросом |
| `mm:<game>` | zset | участник — имя, score — рейтинг | — |
| `room:<id>` | hash | `game`, `players` (JSON), `state` (JSON) | 30 мин, продлевается при `save_state` |
| `events:<id>` | канал pub/sub | JSON-события комнаты | — |
| `cache:<key>` | string | JSON | `ttl` |

## Задачи

| № | Где | Что сделать |
|---|---|---|
| 1 | `sessions.py` | Токен — `secrets.token_urlsafe(32)`; сессия с TTL; `get_session` продлевает TTL (`GETEX`); `drop_session` → `True`, если сессия была. |
| 2 | `allow` | Фиксированное окно: `INCR` и `EXPIRE ... NX` в одной транзакции (`pipeline`). Повторные запросы окно **не** продлевают. |
| 3 | очередь | `enqueue` с `ZADD NX`: повторная постановка → `False`, рейтинг не меняется. `dequeue` → было ли удаление. `queue_size` — `ZCARD`. |
| 4 | `find_match`, `allowed_diff` | Кандидаты — `ZRANGEBYSCORE` в пределах `±max_diff` (границы включительно); ближайший по рейтингу, при равенстве — меньшее имя. Убрать обоих **атомарно** (`pipeline(transaction=True)`); если кто-то уже исчез — вернуть второго в очередь и ответить `None`. Нет игрока в очереди → `LookupError`. |
| 5 | комнаты | `room:<id>` — hash (`HSETNX` на поле `game`: комната уже есть → `ValueError`), TTL; `save_state` продлевает TTL, нет комнаты → `LookupError`. `invite_link` и обратный `room_from_start_param` с проверкой `room_id` по `ROOM_ID`. |
| 6 | pub/sub | `publish` в канал `events:<id>`; `collect` подписывается, собирает `n` сообщений без служебных `subscribe`, по таймауту возвращает сколько есть и **отписывается**. |
| 7* | `cache.py` | `cached` кладёт результат с TTL и не путает пустое значение (`[]`, `0`) с отсутствием в кэше; `invalidate` удаляет ключ. |

Подсказки:
* Задача 4: пока ты между `ZRANGEBYSCORE` и удалением, другая копия сервера может увести того же соперника.
  `ZREM` сообщает, удалил ли он что-то, и по этому понятно, кто успел первым.
* Задача 6: `pubsub = r.pubsub(); await pubsub.subscribe(...)`, затем
  `await pubsub.get_message(ignore_subscribe_messages=True, timeout=0.05)` в цикле под `asyncio.timeout(...)`.
* Заглянуть, что лежит в настоящем Redis: `redis-cli --scan --pattern 'room:*'`, `redis-cli hgetall room:r1`, `ttl room:r1`.

## Проверка у экрана

Показываем в проекте команды: две копии API (`--port 8001` и `--port 8002`) и один Redis. Игроки, подключённые к разным
копиям, находят друг друга в очереди и видят ходы друг друга через pub/sub. Во время партии покажите `redis-cli monitor`.
