# Проект 58 · 9 класс · 2026–2027

<!-- status -->
> **Рабочая версия 1 (29.10.2026): план перерабатывается по итогам встреч менторов, часть решений на согласовании и может измениться.**
<!-- /status -->

Годовой курс школьной ИТ-программы «Проект 58» для 9 класса (8 учеников, 14–15 лет).
За год команда с распределёнными ролями проектирует, пишет, тестирует, разворачивает и сопровождает
**один большой проект — библиотеку мультиплеерных браузерных игр** (идея из кикоффа).
До Нового года — сайт со своим сервером учётных записей; после Нового года к готовым аккаунтам
добавляется вход из Telegram-бота и Mini App. Бэкенд на Python.

* 58 уроков по вторникам и пятницам, 20:00–22:00 МСК: вт 03.11.2026 – вт 08.06.2027, зимние каникулы ~25.12–10.01
  (уроков нет). Даты считаются в [`tools/syllabus.py`](tools/syllabus.py) от первого урока 03.11.
* Т1 — недели 1–5, Т2 — недели 6–16, Т3 — недели 17–29.
* Каждая неделя курса: **лекция** (`l01`) и **семинар** (`l02`), по 3 академических часа. Всего 58 уроков + вводный урок 00.
  До каникул лекция — во вторник, семинар — в пятницу; после каникул пара «лекция + семинар» идёт пт + вт.
* Домашнее задание урока сдаётся до начала следующего урока (срок — в README урока и в таблице ниже).
* Формат занятия: короткая презентационная часть + практические задания для самостоятельной работы на уроке
  (раздел «Практика на уроке» в README урока).
* Стек: Python 3.12, FastAPI, PostgreSQL + SQLAlchemy 2 + Alembic, WebSocket, Docker, Nginx, GitHub Actions, pytest;
  клиент игр — HTML/CSS/JS и `<canvas>`; после Нового года — aiogram 3 (бот и Mini App), Redis.
* Роли в проекте: фронтенд, бэкенд, игровая логика.

## Рабочая версия 1: что изменилось

Решено:

* **Этап 0 — недели 1–9 (до конца декабря): весь код пишем руками.** Агент — только собеседник для объяснений
  («что значит эта строка», «почему ошибка»), его код не вставляем. Это правило главнее раздела
  «Если используете агента» в лабораторных.
* Больше практики: в каждом уроке недель 1–9 — список практических заданий на уроке.
* С урока 02 (пт 06.11) семинар — «Консоль и Git руками»: задания и самопроверка —
  [`lessons/w01-l02-team-setup/practice/console`](lessons/w01-l02-team-setup/practice/console/README.md).
  Пока учебных ВМ нет — работаем на своём ноутбуке (macOS/Linux; Windows — WSL или Git Bash), запасной вариант —
  GitHub Codespaces.
* Один большой проект с ролями фронтенд / бэкенд / игровая логика вместо двух подкоманд по играм.
* Инфраструктура до Нового года: GitHub-организация класса, Wiki, PostgreSQL, свой сервер учётных записей
  (регистрация, хэш паролей, сессии — неделя 3). CI в GitHub Actions — неделя 8; Redis на неделе 8 — только лекция.
* Неделя 5 — демо и срез Т1 + ручной мини-зачёт; неделя 9 — декабрьский ручной зачёт и ретро.
* После Нового года (недели 10–11): Telegram-бот и Mini App как вход к готовым аккаунтам, лобби и матчмейкинг.

На согласовании (может измениться):

* **30.10.2026: даты сдвинуты** — у учеников каникулы, курс начинается во вторник 03.11.2026, уроки по вторникам и
  пятницам 20:00–22:00 МСК. Каникулы ~25.12–10.01 пропускаем, других пропусков пока нет. Из-за сдвига до каникул
  успеваем уроки 01–15 (до 22.12), декабрьский зачёт и ретро (неделя 9) уходят на январь, финал — 08.06.2027;
  праздники 23.02 и весенние каникулы не учтены;

* что агенту можно после декабря (вариант: агент-консультант — объясняет и ревьюит, код не вставляем,
  ученик защищает каждую строку; генерация кода в Т3 — по итогам декабря). Колонка «Агентная разработка»
  недель 10–29 пока оставлена из прежней версии плана;
* сквозные роли (аналитик, тестировщик, девопс) с ротацией;
* какую неделю после Нового года освободить под перенос лобби и бота: убрать R&D Pyodide на неделе 12
  или сжать недели 13–14.

Презентации уроков пока остались прежними: если тема или задания в README урока расходятся с презентацией,
действует README урока.

Источник тем и последовательности — план занятий «Проект 58: план занятий на 2026–2027», переработанный
по итогам встреч менторов 27.10 и 29.10.2026.
Сводка — в [`tools/syllabus.py`](tools/syllabus.py); из него генерируются таблица ниже и README уроков.

## Структура репозитория

```
lessons/
  w00-l00-networks/            вводные лекции о сетях (образец формата, без изменений)
  wNN-l01-<тема>/              лекция недели NN: README.md, lecture.deck → lecture.html
  wNN-l02-<тема>/              семинар недели NN: README.md, seminar.deck → seminar.html
      labs/labXX-<slug>/       лабораторная (если есть): условие, стартовый код, тесты, check.py
      practice/<тема>/         практика на уроке без эталона (например, консоль на уроке 02)
contests/cNN-<тема>/           листы контестов: sheet.md (исходник) → sheet.html, sheet.pdf
solutions/
  labs/labXX-<slug>/           эталонные решения лабораторных (накладываются поверх стартового кода)
  contests/cNN-<тема>/         решения контестов, тесты к ним, заметки для проверки у экрана
rating/                        таблица рейтинга: rating.xlsx (листы контестов + «Рейтинг»), rating.csv
docs/                          правила контестов, формат презентаций, устройство лабораторных
scripts/check_all.sh           проверка лабораторных, контестов и уроков
tools/                         сборка презентаций, листов, README и таблицы рейтинга
```

## Расписание

<!-- schedule -->
Уроки по вторникам и пятницам, 20:00–22:00 МСК; первый урок — вт 03.11.2026. ДЗ урока сдаётся до начала следующего урока.

| Нед. | Дата | Урок | Тема | ДЗ до | Лабораторная | Контест |
|---|---|---|---|---|---|---|
| 1 | вт 03.11 | [01 · Лекция](lessons/w01-l01-kickoff/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w01-l01-kickoff/lecture.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w01-l01-kickoff/lecture.html#download) | Кикофф: игры из Telegram, роли, Git-процесс | пт 06.11 |  |  |
| 1 | пт 06.11 | [02 · Семинар](lessons/w01-l02-team-setup/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w01-l02-team-setup/seminar.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w01-l02-team-setup/seminar.html#download) | Семинар: Консоль и Git руками | вт 10.11 | [lab01](lessons/w01-l02-team-setup/labs/lab01-git-flow/README.md) |  |
| 2 | вт 10.11 | [03 · Лекция](lessons/w02-l01-spec-first/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w02-l01-spec-first/lecture.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w02-l01-spec-first/lecture.html#download) | Spec-first: user story, критерии приёмки, протокол API; архитектура проекта | пт 13.11 |  |  |
| 2 | пт 13.11 | [04 · Семинар](lessons/w02-l02-bot-and-api/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w02-l02-bot-and-api/seminar.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w02-l02-bot-and-api/seminar.html#download) | Семинар: спека игры 1, контракт API между ролями, каркас FastAPI руками | вт 17.11 | [lab02](lessons/w02-l02-bot-and-api/labs/lab02-api-by-spec/README.md) | [c01](contests/c01-python-git-specs/sheet.pdf) · [открыть](https://tilzziter.github.io/p58-course-2026/contests/c01-python-git-specs/sheet.html) · [скачать](https://tilzziter.github.io/p58-course-2026/contests/c01-python-git-specs/sheet.html#download) |
| 3 | вт 17.11 | [05 · Лекция](lessons/w03-l01-mini-apps/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w03-l01-mini-apps/lecture.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w03-l01-mini-apps/lecture.html#download) | Сервер учётных записей v0: регистрация, хэш паролей, сессии; подпись данных HMAC; canvas | пт 20.11 | [lab03](lessons/w03-l01-mini-apps/labs/lab03-init-data/README.md) |  |
| 3 | пт 20.11 | [06 · Семинар](lessons/w03-l02-game-logic/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w03-l02-game-logic/seminar.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w03-l02-game-logic/seminar.html#download) | Семинар: логика «4 в ряд» на сервере, pytest, отрисовка на canvas | вт 24.11 | [lab04](lessons/w03-l02-game-logic/labs/lab04-connect-four/README.md) |  |
| 4 | вт 24.11 | [07 · Лекция](lessons/w04-l01-docker-nginx/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w04-l01-docker-nginx/lecture.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w04-l01-docker-nginx/lecture.html#download) | Docker и docker compose; Nginx как reverse proxy, домен, HTTPS | пт 27.11 |  |  |
| 4 | пт 27.11 | [08 · Семинар](lessons/w04-l02-deploy-mvp/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w04-l02-deploy-mvp/seminar.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w04-l02-deploy-mvp/seminar.html#download) | Семинар: деплой MVP на VPS, чек-лист DevOps, репетиция демо | вт 01.12 | [lab05](lessons/w04-l02-deploy-mvp/labs/lab05-docker-review/README.md) | [c02](contests/c02-grids-games-signatures/sheet.pdf) · [открыть](https://tilzziter.github.io/p58-course-2026/contests/c02-grids-games-signatures/sheet.html) · [скачать](https://tilzziter.github.io/p58-course-2026/contests/c02-grids-games-signatures/sheet.html#download) |
| 5 | вт 01.12 | [09 · Лекция](lessons/w05-l01-review-t1/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w05-l01-review-t1/lecture.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w05-l01-review-t1/lecture.html#download) | Повторение к срезу Т1, ручной мини-зачёт, ретро триместра | пт 04.12 |  |  |
| 5 | пт 04.12 | [10 · Семинар](lessons/w05-l02-demo-t1/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w05-l02-demo-t1/seminar.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w05-l02-demo-t1/seminar.html#download) | Демо Т1 для родителей и администрации; срез Т1 | — |  |  |
| 6 | вт 08.12 | [11 · Лекция](lessons/w06-l01-websocket-asyncio/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w06-l01-websocket-asyncio/lecture.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w06-l01-websocket-asyncio/lecture.html#download) | WebSocket в FastAPI, asyncio; комнаты и протокол сообщений | пт 11.12 |  |  |
| 6 | пт 11.12 | [12 · Семинар](lessons/w06-l02-multiplayer-rooms/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w06-l02-multiplayer-rooms/seminar.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w06-l02-multiplayer-rooms/seminar.html#download) | Семинар: мультиплеер игры 1, комната на 2 игрока, сервер — источник истины | вт 15.12 | [lab06](lessons/w06-l02-multiplayer-rooms/labs/lab06-ws-rooms/README.md) | [c03](contests/c03-asyncio-protocols/sheet.pdf) · [открыть](https://tilzziter.github.io/p58-course-2026/contests/c03-asyncio-protocols/sheet.html) · [скачать](https://tilzziter.github.io/p58-course-2026/contests/c03-asyncio-protocols/sheet.html#download) |
| 7 | вт 15.12 | [13 · Лекция](lessons/w07-l01-postgres-sqlalchemy/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w07-l01-postgres-sqlalchemy/lecture.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w07-l01-postgres-sqlalchemy/lecture.html#download) | PostgreSQL вместо SQLite: SQLAlchemy 2 (async), миграции Alembic | пт 18.12 |  |  |
| 7 | пт 18.12 | [14 · Семинар](lessons/w07-l02-db-rating/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w07-l02-db-rating/seminar.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w07-l02-db-rating/seminar.html#download) | Семинар: аккаунты, партии и рейтинг в PostgreSQL; история партий | вт 22.12 | [lab07](lessons/w07-l02-db-rating/labs/lab07-sqlalchemy-rating/README.md) |  |
| 8 | вт 22.12 | [15 · Лекция](lessons/w08-l01-redis/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w08-l01-redis/lecture.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w08-l01-redis/lecture.html#download) | Redis: сессии, TTL, pub/sub — обзорная лекция (лобби и матчмейкинг — после Нового года) | вт 12.01 |  |  |
| — | 25.12–10.01 | — | **Зимние каникулы** (ориентировочно); по желанию — QuestHub | — | — | — |
| 8 | вт 12.01 | [16 · Семинар](lessons/w08-l02-lobby-matchmaking/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w08-l02-lobby-matchmaking/seminar.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w08-l02-lobby-matchmaking/seminar.html#download) | Семинар: CI в GitHub Actions руками — ruff и pytest на каждый PR (лобби — после Нового года) | пт 15.01 | [lab08](lessons/w08-l02-lobby-matchmaking/labs/lab08-redis-matchmaking/README.md) | [c04](contests/c04-databases-cache/sheet.pdf) · [открыть](https://tilzziter.github.io/p58-course-2026/contests/c04-databases-cache/sheet.html) · [скачать](https://tilzziter.github.io/p58-course-2026/contests/c04-databases-cache/sheet.html#download) |
| 9 | пт 15.01 | [17 · Лекция](lessons/w09-l01-ci-github-actions/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w09-l01-ci-github-actions/lecture.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w09-l01-ci-github-actions/lecture.html#download) | CI: сборка образа; повторение к декабрьскому ручному зачёту | вт 19.01 | [lab09](lessons/w09-l01-ci-github-actions/labs/lab09-ci-pipeline/README.md) |  |
| 9 | вт 19.01 | [18 · Семинар](lessons/w09-l02-pr-review-retro/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w09-l02-pr-review-retro/seminar.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w09-l02-pr-review-retro/seminar.html#download) | Семинар: декабрьский ручной зачёт, ревью PR, ретро полугодия | — |  |  |
| 10 | пт 22.01 | [19 · Лекция](lessons/w10-l01-cd-deploy/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w10-l01-cd-deploy/lecture.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w10-l01-cd-deploy/lecture.html#download) | CD: автодеплой на VPS после merge, секреты, staging и prod | вт 26.01 | [lab10](lessons/w10-l01-cd-deploy/labs/lab10-secret-scanner/README.md) |  |
| 10 | вт 26.01 | [20 · Семинар](lessons/w10-l02-deploy-pipeline/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w10-l02-deploy-pipeline/seminar.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w10-l02-deploy-pipeline/seminar.html#download) | Семинар: пайплайн деплоя; Telegram-бот и Mini App как вход к готовым аккаунтам | пт 29.01 |  | [c05](contests/c05-pipelines-secrets/sheet.pdf) · [открыть](https://tilzziter.github.io/p58-course-2026/contests/c05-pipelines-secrets/sheet.html) · [скачать](https://tilzziter.github.io/p58-course-2026/contests/c05-pipelines-secrets/sheet.html#download) |
| 11 | пт 29.01 | [21 · Лекция](lessons/w11-l01-game-algorithms/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w11-l01-game-algorithms/lecture.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w11-l01-game-algorithms/lecture.html#download) | Алгоритмы игры 2: игровой цикл, конечный автомат, честный рандом, коллизии | вт 02.02 | [lab11](lessons/w11-l01-game-algorithms/labs/lab11-snake-engine/README.md) |  |
| 11 | вт 02.02 | [22 · Семинар](lessons/w11-l02-game2-spec/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w11-l02-game2-spec/seminar.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w11-l02-game2-spec/seminar.html#download) | Семинар: спека и серверная логика игры 2; лобби и матчмейкинг (перенос с недели 8) | пт 05.02 |  |  |
| 12 | пт 05.02 | [23 · Лекция](lessons/w12-l01-game-frontend/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w12-l01-game-frontend/lecture.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w12-l01-game-frontend/lecture.html#download) | Фронтенд игр: requestAnimationFrame, интерполяция, тема Telegram, мобильная вёрстка; Pyodide | вт 09.02 |  |  |
| 12 | вт 09.02 | [24 · Семинар](lessons/w12-l02-game2-client/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w12-l02-game2-client/seminar.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w12-l02-game2-client/seminar.html#download) | Семинар: клиент игры 2, UI-кит, R&D-прототип на Pyodide | пт 12.02 | [lab12](lessons/w12-l02-game2-client/labs/lab12-interpolation/README.md) | [c06](contests/c06-game-loop-random/sheet.pdf) · [открыть](https://tilzziter.github.io/p58-course-2026/contests/c06-game-loop-random/sheet.html) · [скачать](https://tilzziter.github.io/p58-course-2026/contests/c06-game-loop-random/sheet.html#download) |
| 13 | пт 12.02 | [25 · Лекция](lessons/w13-l01-testing/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w13-l01-testing/lecture.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w13-l01-testing/lecture.html#download) | Тестирование: pytest-asyncio, тесты WebSocket, тестовая БД, смоук e2e | вт 16.02 | [lab13](lessons/w13-l01-testing/labs/lab13-mutation-tests/README.md) |  |
| 13 | вт 16.02 | [26 · Семинар](lessons/w13-l02-qa-plan/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w13-l02-qa-plan/seminar.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w13-l02-qa-plan/seminar.html#download) | Семинар: QA-план, баг-трекинг, тесты в CI, метрики работы агента | пт 19.02 |  |  |
| 14 | пт 19.02 | [27 · Лекция](lessons/w14-l01-monitoring/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w14-l01-monitoring/lecture.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w14-l01-monitoring/lecture.html#download) | Мониторинг и логи: структурированные логи, healthcheck, метрики, алерты в Telegram | вт 23.02 | [lab14](lessons/w14-l01-monitoring/labs/lab14-logs-alerts/README.md) |  |
| 14 | вт 23.02 | [28 · Семинар](lessons/w14-l02-incident-drill/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w14-l02-incident-drill/seminar.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w14-l02-incident-drill/seminar.html#download) | Семинар: дашборд и алерты; учение «сайт упал» | пт 26.02 |  | [c07](contests/c07-tests-logs/sheet.pdf) · [открыть](https://tilzziter.github.io/p58-course-2026/contests/c07-tests-logs/sheet.html) · [скачать](https://tilzziter.github.io/p58-course-2026/contests/c07-tests-logs/sheet.html#download) |
| 15 | пт 26.02 | [29 · Лекция](lessons/w15-l01-security/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w15-l01-security/lecture.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w15-l01-security/lecture.html#download) | Безопасность и ответственность: античит, rate limit, данные пользователей, prompt injection | вт 02.03 | [lab15](lessons/w15-l01-security/labs/lab15-anticheat-ratelimit/README.md) |  |
| 15 | вт 02.03 | [30 · Семинар](lessons/w15-l02-security-audit/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w15-l02-security-audit/seminar.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w15-l02-security-audit/seminar.html#download) | Семинар: аудит безопасности, feature freeze | пт 05.03 |  |  |
| 16 | пт 05.03 | [31 · Лекция](lessons/w16-l01-review-t2/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w16-l01-review-t2/lecture.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w16-l01-review-t2/lecture.html#download) | Повторение к срезу Т2, ретро триместра | вт 09.03 |  |  |
| 16 | вт 09.03 | [32 · Семинар](lessons/w16-l02-demo-t2/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w16-l02-demo-t2/seminar.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w16-l02-demo-t2/seminar.html#download) | Демо Т2 и срез Т2 | пт 12.03 |  | [c08](contests/c08-security/sheet.pdf) · [открыть](https://tilzziter.github.io/p58-course-2026/contests/c08-security/sheet.html) · [скачать](https://tilzziter.github.io/p58-course-2026/contests/c08-security/sheet.html#download) |
| 17 | пт 12.03 | [33 · Лекция](lessons/w17-l01-llm-in-product/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w17-l01-llm-in-product/lecture.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w17-l01-llm-in-product/lecture.html#download) | LLM в продукте: API модели, промпты, ограничения, модерация | вт 16.03 | [lab16](lessons/w17-l01-llm-in-product/labs/lab16-llm-evals/README.md) |  |
| 17 | вт 16.03 | [34 · Семинар](lessons/w17-l02-extension-spec/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w17-l02-extension-spec/seminar.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w17-l02-extension-spec/seminar.html#download) | Семинар: выбор расширения и его спека, набор evals | пт 19.03 |  |  |
| 18 | пт 19.03 | [35 · Лекция](lessons/w18-l01-hackathon-format/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w18-l01-hackathon-format/lecture.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w18-l01-hackathon-format/lecture.html#download) | Формат хакатона: шаблон проекта, роли под таймер, питч | вт 23.03 |  |  |
| 18 | вт 23.03 | [36 · Семинар](lessons/w18-l02-project-template/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w18-l02-project-template/seminar.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w18-l02-project-template/seminar.html#download) | Семинар: шаблон «FastAPI + бот + Docker» за одну сессию | пт 26.03 |  | [c09](contests/c09-texts-prompts-templates/sheet.pdf) · [открыть](https://tilzziter.github.io/p58-course-2026/contests/c09-texts-prompts-templates/sheet.html) · [скачать](https://tilzziter.github.io/p58-course-2026/contests/c09-texts-prompts-templates/sheet.html#download) |
| 19 | пт 26.03 | [37 · Лекция](lessons/w19-l01-mini-hackathon-1/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w19-l01-mini-hackathon-1/lecture.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w19-l01-mini-hackathon-1/lecture.html#download) | Мини-хакатон, сессия 1: идея, спека, каркас | — |  |  |
| 19 | вт 30.03 | [38 · Семинар](lessons/w19-l02-mini-hackathon-2/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w19-l02-mini-hackathon-2/seminar.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w19-l02-mini-hackathon-2/seminar.html#download) | Мини-хакатон, сессия 2: доделка, питч, жюри | пт 02.04 |  |  |
| 20 | пт 02.04 | [39 · Лекция](lessons/w20-l01-data-analysis/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w20-l01-data-analysis/lecture.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w20-l01-data-analysis/lecture.html#download) | Анализ данных: pandas, SQL-аналитика, графики | вт 06.04 | [lab17](lessons/w20-l01-data-analysis/labs/lab17-game-analytics/README.md) |  |
| 20 | вт 06.04 | [40 · Семинар](lessons/w20-l02-game-metrics/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w20-l02-game-metrics/seminar.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w20-l02-game-metrics/seminar.html#download) | Семинар: аналитика игровых событий — удержание, длина партий, баланс | пт 09.04 |  | [c10](contests/c10-data-metrics/sheet.pdf) · [открыть](https://tilzziter.github.io/p58-course-2026/contests/c10-data-metrics/sheet.html) · [скачать](https://tilzziter.github.io/p58-course-2026/contests/c10-data-metrics/sheet.html#download) |
| 21 | пт 09.04 | [41 · Лекция](lessons/w21-l01-game-ai/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w21-l01-game-ai/lecture.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w21-l01-game-ai/lecture.html#download) | Алгоритмы ИИ-соперника: минимакс, эвристики, Монте-Карло | вт 13.04 | [lab18](lessons/w21-l01-game-ai/labs/lab18-minimax/README.md) |  |
| 21 | вт 13.04 | [42 · Семинар](lessons/w21-l02-ai-opponent/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w21-l02-ai-opponent/seminar.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w21-l02-ai-opponent/seminar.html#download) | Семинар: бот-соперник в одной из игр, турнир решений | пт 16.04 |  |  |
| 22 | пт 16.04 | [43 · Лекция](lessons/w22-l01-load-scaling/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w22-l01-load-scaling/lecture.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w22-l01-load-scaling/lecture.html#download) | Нагрузка и масштабирование: locust, реплики за Nginx, Redis pub/sub, индексы | вт 20.04 | [lab19](lessons/w22-l01-load-scaling/labs/lab19-load-report/README.md) |  |
| 22 | вт 20.04 | [44 · Семинар](lessons/w22-l02-load-test/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w22-l02-load-test/seminar.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w22-l02-load-test/seminar.html#download) | Семинар: нагрузочный тест и оптимизация | пт 23.04 |  | [c11](contests/c11-game-trees/sheet.pdf) · [открыть](https://tilzziter.github.io/p58-course-2026/contests/c11-game-trees/sheet.html) · [скачать](https://tilzziter.github.io/p58-course-2026/contests/c11-game-trees/sheet.html#download) |
| 23 | пт 23.04 | [45 · Лекция](lessons/w23-l01-hackathon-window/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w23-l01-hackathon-window/lecture.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w23-l01-hackathon-window/lecture.html#download) | Окно внешнего хакатона: подготовка и участие | вт 27.04 |  |  |
| 23 | вт 27.04 | [46 · Семинар](lessons/w23-l02-hackathon-retro/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w23-l02-hackathon-retro/seminar.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w23-l02-hackathon-retro/seminar.html#download) | Семинар: ретро хакатона, буфер, опционально QuestHub | — |  |  |
| 24 | пт 30.04 | [47 · Лекция](lessons/w24-l01-extension-cycle/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w24-l01-extension-cycle/lecture.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w24-l01-extension-cycle/lecture.html#download) | Расширение продукта: полный цикл spec-first | вт 04.05 |  |  |
| 24 | вт 04.05 | [48 · Семинар](lessons/w24-l02-extension-impl/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w24-l02-extension-impl/seminar.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w24-l02-extension-impl/seminar.html#download) | Семинар: реализация расширения по мартовской спеке | пт 07.05 |  | [c12](contests/c12-load-scale/sheet.pdf) · [открыть](https://tilzziter.github.io/p58-course-2026/contests/c12-load-scale/sheet.html) · [скачать](https://tilzziter.github.io/p58-course-2026/contests/c12-load-scale/sheet.html#download) |
| 25 | пт 07.05 | [49 · Лекция](lessons/w25-l01-ux-accessibility/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w25-l01-ux-accessibility/lecture.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w25-l01-ux-accessibility/lecture.html#download) | UX: юзабилити-тесты, доступность | вт 11.05 |  |  |
| 25 | вт 11.05 | [50 · Семинар](lessons/w25-l02-usability-tests/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w25-l02-usability-tests/seminar.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w25-l02-usability-tests/seminar.html#download) | Семинар: тесты на одноклассниках, правки интерфейса | пт 14.05 |  |  |
| 26 | пт 14.05 | [51 · Лекция](lessons/w26-l01-backups-runbook/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w26-l01-backups-runbook/lecture.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w26-l01-backups-runbook/lecture.html#download) | Надёжность: бэкапы PostgreSQL, восстановление, runbook | вт 18.05 | [lab20](lessons/w26-l01-backups-runbook/labs/lab20-backups/README.md) |  |
| 26 | вт 18.05 | [52 · Семинар](lessons/w26-l02-restore-drill/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w26-l02-restore-drill/seminar.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w26-l02-restore-drill/seminar.html#download) | Семинар: учение по восстановлению; feature freeze | пт 21.05 |  | [c13](contests/c13-reliability-time/sheet.pdf) · [открыть](https://tilzziter.github.io/p58-course-2026/contests/c13-reliability-time/sheet.html) · [скачать](https://tilzziter.github.io/p58-course-2026/contests/c13-reliability-time/sheet.html#download) |
| 27 | пт 21.05 | [53 · Лекция](lessons/w27-l01-docs-portfolio/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w27-l01-docs-portfolio/lecture.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w27-l01-docs-portfolio/lecture.html#download) | Документация и портфолио: README, архитектура, видео-демо | вт 25.05 |  |  |
| 27 | вт 25.05 | [54 · Семинар](lessons/w27-l02-stabilization/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w27-l02-stabilization/seminar.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w27-l02-stabilization/seminar.html#download) | Семинар: стабилизация, багфиксы, release candidate | пт 28.05 |  |  |
| 28 | пт 28.05 | [55 · Лекция](lessons/w28-l01-pitch/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w28-l01-pitch/lecture.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w28-l01-pitch/lecture.html#download) | Публичное выступление и питч | вт 01.06 |  |  |
| 28 | вт 01.06 | [56 · Семинар](lessons/w28-l02-rehearsal/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w28-l02-rehearsal/seminar.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w28-l02-rehearsal/seminar.html#download) | Семинар: генеральный прогон финального демо | пт 04.06 |  | [c14](contests/c14-season-final/sheet.pdf) · [открыть](https://tilzziter.github.io/p58-course-2026/contests/c14-season-final/sheet.html) · [скачать](https://tilzziter.github.io/p58-course-2026/contests/c14-season-final/sheet.html#download) |
| 29 | пт 04.06 | [57 · Лекция](lessons/w29-l01-final-review/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w29-l01-final-review/lecture.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w29-l01-final-review/lecture.html#download) | Итоговое повторение | вт 08.06 |  |  |
| 29 | вт 08.06 | [58 · Семинар](lessons/w29-l02-final-demo/README.md) · [слайды](https://tilzziter.github.io/p58-course-2026/lessons/w29-l02-final-demo/seminar.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w29-l02-final-demo/seminar.html#download) | Финальный демо-день, срез Т3, ретро года | — |  |  |
<!-- /schedule -->

## Как открыть материалы

* Презентация — просто откройте `lecture.html` / `seminar.html` в браузере. ← / → — листать, **T** — простой и
  технический режим, **A** — ответы, **G** — оглавление, **F** — полный экран. Работает без интернета.
* Лист контеста — `contests/<id>/sheet.pdf`.

## Как запускать лабораторные

```bash
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
cd lessons/w01-l02-team-setup/labs/lab01-git-flow
python check.py                      # таблица задач: OK / НЕТ
python check.py -v 3                 # подробности по задаче 3
```

Лабораторные работают без серверов: FastAPI и WebSocket — через `TestClient`, база — SQLite в памяти,
Redis — `fakeredis`. Подробнее — [`docs/labs.md`](docs/labs.md).

## Контесты

Раз в две недели, на семинаре чётной недели; 14 контестов, сезон 1 — контесты 1–4 (до Нового года),
сезон 2 — контесты 5–14. Обычная задача — 2 монеты, со звёздочкой — 4, часть босса — 6.
Полные правила — [`docs/contest-rules.md`](docs/contest-rules.md), таблица — [`rating/rating.xlsx`](rating/rating.xlsx).

## Где решения

Репозиторий публичный и содержит всё, включая решения. Решения лежат в отдельной корневой папке
[`solutions/`](solutions/) и никогда — рядом со стартовым кодом учеников.

## Для преподавателя: учебный сервер

* Ученики работают на учебном Linux-сервере курса (логины `p58-sNN`, преподаватели — `p58-tNN`). Адрес и пароли
  в репозиторий не кладём: раздаём лично, у каждого временный пароль, при первом входе сервер требует сменить его.
* Ученики начинают с **шага 0** [лабораторной 01](lessons/w01-l02-team-setup/labs/lab01-git-flow/README.md):
  вход и SSH-ключ → клон общей репы → своя ветка `<ник>/lab01` → задачи → `check.py` → коммиты и push → PR в `main`.
  Каждый шаг ссылается на раздел
  инструкции [`docs/server-windows.md`](docs/server-windows.md) (Windows; она же выгружается ученикам).
* Преподаватели проходят те же шаги со своим логином (разделы 1–6 инструкции) — так проще помогать у экрана.
* Преподаватели (группа `p58-teachers`) могут **читать** домашние папки учеников: `ls /home/p58-sNN/p58-course-labs`.
  Менять не могут; `~/.ssh` учеников закрыта.
* Сдача (пока — лабораторная 01): без форков. Ученики — участники репы `school58-project/p58-course-labs`
  с правом записи (приглашает Саша), каждый пушит ветку `<ник>/lab01` и открывает PR в `main`. `main` защищена:
  только через PR с одобрением, без force-push и удаления; на админов защита не распространяется, поэтому выгрузку
  материалов в `main` пушит владелец репы как раньше. Проверка — `python tools/check_prs.py --lab lab01`
  (PR в `main`, ветки `*/lab01`, последний PR каждого автора, предупреждение о чужих коммитах; тесты — из `main`).
* `~/.ssh` у всех учётных записей — `700` без ACL (иначе ACL для преподавателей наследовался в ключи, они получали
  права `640` и SSH их отбрасывал). Новые учётные записи — только через `sudo p58-adduser <логин> student|teacher`
  на сервере; починить права существующим — `sudo p58-fix-ssh-perms`. В инструкции после `ssh-keygen` оставлен
  `chmod 600 ~/.ssh/id_ed25519` на всякий случай.

## Для преподавателя: сборка и проверка

```bash
make decks       # .deck → .html
make contests    # sheet.md → sheet.html + sheet.pdf (нужен Google Chrome или Chromium)
make readmes     # README уроков и таблица расписания
make rating      # rating/rating.xlsx
make check       # стартовый код падает, эталоны проходят, уроки собраны
```
