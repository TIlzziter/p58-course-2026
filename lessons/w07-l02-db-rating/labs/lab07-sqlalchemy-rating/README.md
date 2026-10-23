# Лабораторная 07. Рейтинг на SQLAlchemy

Переносим рейтинг игроков из памяти в базу данных. Код один и тот же для SQLite (разработка и тесты) и
PostgreSQL (в `docker compose`) — меняется только `DATABASE_URL`.

| Файл | Что внутри | Статус |
|---|---|---|
| `db.py` | создание async-движка, `PRAGMA foreign_keys` для SQLite | готово |
| `models.py` | таблицы `players` и `matches` | задача 1 |
| `elo.py` | формула Эло | задача 2 |
| `repo.py` | запросы: игроки, партии, таблица лидеров, история | задачи 3–6 |
| `migrations/` | Alembic: `env.py` готов, миграция `0001` написана агентом | задача 7 |
| `app.py` | HTTP API поверх `repo.py` | задача 8* |

```bash
pip install -r ../../../../requirements.txt     # один раз, из корня курса
python check.py           # все задачи
python check.py -v 4      # подробности по задаче 4
```

Задачи 3–6 опираются на модели: пока не сделана задача 1, их тесты падают с `IntegrityError`.

## Схема

```text
players                          matches
  id          PK                   id           PK
  tg_id       BIGINT, UNIQUE       game         VARCHAR(32)
  name        VARCHAR(64)          player1_id   FK → players.id, ON DELETE CASCADE, индекс
  rating      INT, по умолч. 1000  player2_id   FK → players.id, ON DELETE CASCADE, индекс
  created_at  DATETIME now()       result       'win1' | 'win2' | 'draw'   (CHECK)
                                   delta1, delta2  изменение рейтинга игроков
                                   played_at    DATETIME now(), индекс
                                   CHECK player1_id <> player2_id
```

## Задачи

| № | Где | Что сделать |
|---|---|---|
| 1 | `models.py` | `tg_id` уникален; `rating` по умолчанию 1000 (`default` и `server_default`); CHECK-ограничения `ck_matches_result` и `ck_matches_two_players`; `ondelete="CASCADE"` и индексы на внешних ключах; индекс на `played_at`. |
| 2 | `elo.py` | `expected(ra, rb) = 1 / (1 + 10 ** ((rb − ra) / 400))`. `update` считает `delta = round(k · (score − expected))` **один раз**: A получает `+delta`, B — `−delta`, рейтинги целые, сумма не меняется. `score` не из {0, 0.5, 1} → `ValueError`. |
| 3 | `get_or_create_player` | Найти по `tg_id` (`select ... where`); нет — создать и `flush()`, чтобы появился `id`; есть — обновить имя. |
| 4 | `record_match` | Проверить результат и что игроки разные (`ValueError`), нет игрока → `LookupError`. Посчитать Эло, сохранить матч с `delta1/delta2`, обновить рейтинги. **Без commit** — его делает вызывающий код. |
| 5 | `leaderboard` | Только сыгравшие хотя бы одну партию; партии считаются за **обе** стороны (`or_`); сортировка: рейтинг ↓, партии ↓, имя ↑. |
| 6 | `history` | Партии игрока новыми первыми (`played_at`, затем `id` — время может совпасть), с его точки зрения: `{"game", "opponent", "result": "win"/"loss"/"draw", "delta"}`. Имена обоих игроков — через `aliased(Player)`. |
| 7 | `migrations/versions/0001_initial.py` | Ревью миграции агента: тест сравнивает базу после `alembic upgrade head` с моделями (`compare_metadata`) и проверяет, что `downgrade base` удаляет всё. Найдите и исправьте расхождения. |
| 8* | `app.py` | `POST /matches` (оба игрока создаются при необходимости, всё в одной транзакции `async with session.begin()`; один и тот же игрок → 400), `GET /leaderboard?limit=`, `GET /players/{tg_id}/history` (нет игрока → 404). |

Подсказки:
* `await session.scalar(select(Player).where(Player.tg_id == tg_id))` — один объект или `None`.
* Посмотреть SQL, который генерирует SQLAlchemy: `make_engine(url, echo=True)`.
* Задача 7: `alembic upgrade head`, затем `alembic check` (или `alembic revision --autogenerate -m test` — и посмотрите,
  что агент «забыл»). Порядок в `downgrade` — обратный порядку создания.

## Миграции руками

```bash
export DATABASE_URL=sqlite+aiosqlite:///rating.db
alembic upgrade head                                   # создать таблицы
alembic revision --autogenerate -m "add avatar"        # после изменения models.py
alembic downgrade -1                                   # откатить последнюю
```

С PostgreSQL из compose: `DATABASE_URL=postgresql+asyncpg://game:secret@localhost:5432/game` (для миграций
`env.py` сам подставит синхронный драйвер `psycopg`).

## Проверка у экрана

Покажите `alembic upgrade head` на чистой базе, таблицу лидеров после трёх партий (`sqlite3 rating.db` или
`psql`: `SELECT name, rating FROM players ORDER BY rating DESC;`) и найденные в миграции агента ошибки.
