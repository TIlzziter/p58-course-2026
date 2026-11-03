# Урок 08. Семинар: деплой MVP на VPS, чек-лист DevOps, репетиция демо

> Рабочая версия 1 (29.10.2026): план перерабатывается по итогам встреч менторов, часть решений на согласовании и может измениться.

**Неделя 4** (24.11–27.11) · Триместр 1 · Семинар · 3 академических часа

**Дата:** пт 27.11.2026, 20:00–22:00 МСК

**▶ [Открыть семинар в браузере](https://tilzziter.github.io/p58-course-2026/lessons/w04-l02-deploy-mvp/seminar.html)** · [⤓ Скачать](https://tilzziter.github.io/p58-course-2026/lessons/w04-l02-deploy-mvp/seminar.html#download)

## Цели

- развернуть MVP на VPS через compose: сайт, сервер учётных записей, логика игры
- проверить свои конфиги по чек-листу DevOps
- отрепетировать демо Т1

## Практика на уроке

Формат занятия: короткая презентационная часть + практические задания для самостоятельной работы на уроке.

1. руками: `git pull` и `docker compose up -d` на сервере, разбор `docker compose logs`
2. проверить HTTPS и регистрацию на настоящем домене
3. проверить свои Dockerfile и compose по чек-листу и исправить 2 замечания
4. прогон демо: по 3 минуты на роль

## Материалы

- Семинар: презентация — [открыть в браузере](https://tilzziter.github.io/p58-course-2026/lessons/w04-l02-deploy-mvp/seminar.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w04-l02-deploy-mvp/seminar.html#download); файл [`seminar.html`](seminar.html), исходник [`seminar.deck`](seminar.deck)
- Лабораторная: [`labs/lab05-docker-review`](labs/lab05-docker-review/README.md) — автопроверка `python check.py`; эталон — `solutions/labs/lab05-docker-review/`
- Контест 2 «Сетки, игры и подписи» (сезон 1): [лист PDF](../../contests/c02-grids-games-signatures/sheet.pdf) ([открыть в браузере](https://tilzziter.github.io/p58-course-2026/contests/c02-grids-games-signatures/sheet.html) · [скачать](https://tilzziter.github.io/p58-course-2026/contests/c02-grids-games-signatures/sheet.html#download)), [исходник](../../contests/c02-grids-games-signatures/sheet.md); решения — `solutions/contests/c02-grids-games-signatures/`

## Агентная разработка

Этап 0: агент только объясняет; код руками. Спросить у агента: «что значит эта строка в логах», «почему порт занят». Руками: деплой и исправления по чек-листу делаем сами.

До конца декабря раздел лабораторной «Если используете агента» читаем по правилу этапа 0: агента можно спрашивать, что значит код или ошибка, но код пишем сами.

## Домашнее задание

Лабораторная 05 «Ревью Docker-конфигов» + контест 2.

**Срок:** до начала урока 09 — вт 01.12.2026, 20:00 МСК.

**Результат недели по плану:** MVP (сайт, сервер учётных записей, «4 в ряд») работает по HTTPS; репетиция демо
