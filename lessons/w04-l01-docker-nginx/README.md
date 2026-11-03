# Урок 07. Docker и docker compose; Nginx как reverse proxy, домен, HTTPS

> Рабочая версия 1 (29.10.2026): план перерабатывается по итогам встреч менторов, часть решений на согласовании и может измениться.

**Неделя 4** (24.11–27.11) · Триместр 1 · Лекция · 3 академических часа

**Дата:** вт 24.11.2026, 20:00–22:00 МСК

**▶ [Открыть лекцию в браузере](https://tilzziter.github.io/p58-course-2026/lessons/w04-l01-docker-nginx/lecture.html)** · [⤓ Скачать](https://tilzziter.github.io/p58-course-2026/lessons/w04-l01-docker-nginx/lecture.html#download)

## Цели

- понимать образ, контейнер, слой, volume, сеть compose
- собрать compose: сайт + сервер учётных записей + игровая логика + nginx
- настроить reverse proxy и HTTPS-сертификат

## Практика на уроке

Формат занятия: короткая презентационная часть + практические задания для самостоятельной работы на уроке.

1. руками: `Dockerfile` своего сервиса, `docker build` и `docker run`
2. руками: `docker compose up` для двух сервисов, проверить `curl` по сети compose
3. найти в образце Dockerfile 3 ошибки по чек-листу DevOps (секреты, размер, порядок слоёв)

## Материалы

- Лекция: презентация — [открыть в браузере](https://tilzziter.github.io/p58-course-2026/lessons/w04-l01-docker-nginx/lecture.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w04-l01-docker-nginx/lecture.html#download); файл [`lecture.html`](lecture.html), исходник [`lecture.deck`](lecture.deck)

## Агентная разработка

Этап 0: агент только объясняет; код руками. Спросить у агента: «чем образ отличается от контейнера», «зачем `.dockerignore`». Руками: Dockerfile и compose пишем сами и проверяем по чек-листу DevOps.

## Домашнее задание

Прочитать чек-лист DevOps, дописать Dockerfile своего сервиса руками.

**Срок:** до начала урока 08 — пт 27.11.2026, 20:00 МСК.

**Результат недели по плану:** MVP (сайт, сервер учётных записей, «4 в ряд») работает по HTTPS; репетиция демо
