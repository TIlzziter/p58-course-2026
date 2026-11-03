# Урок 51. Надёжность: бэкапы PostgreSQL, восстановление, runbook

> Рабочая версия 1 (29.10.2026): план перерабатывается по итогам встреч менторов, часть решений на согласовании и может измениться.

**Неделя 26** (14.05–18.05) · Триместр 3 · Лекция · 3 академических часа

**Дата:** пт 14.05.2027, 20:00–22:00 МСК

**▶ [Открыть лекцию в браузере](https://tilzziter.github.io/p58-course-2026/lessons/w26-l01-backups-runbook/lecture.html)** · [⤓ Скачать](https://tilzziter.github.io/p58-course-2026/lessons/w26-l01-backups-runbook/lecture.html#download)

## Цели

- RPO и RTO
- pg_dump и восстановление
- ротация бэкапов
- runbook

## Материалы

- Лекция: презентация — [открыть в браузере](https://tilzziter.github.io/p58-course-2026/lessons/w26-l01-backups-runbook/lecture.html) · [скачать](https://tilzziter.github.io/p58-course-2026/lessons/w26-l01-backups-runbook/lecture.html#download); файл [`lecture.html`](lecture.html), исходник [`lecture.deck`](lecture.deck)
- Лабораторная: [`labs/lab20-backups`](labs/lab20-backups/README.md) — автопроверка `python check.py`; эталон — `solutions/labs/lab20-backups/`

## Агентная разработка

> На согласовании: правила использования агента после декабря. Вариант — агент-консультант: объясняет и ревьюит, его код не вставляем, ученик защищает каждую строку; генерация кода в Т3 — по итогам декабря. Текст ниже — из прежней версии плана.

Агент пишет runbook, DevOps проверяет его «вслепую»

## Домашнее задание

Лабораторная 20 «Бэкапы и восстановление».

**Срок:** до начала урока 52 — вт 18.05.2027, 20:00 МСК.

**Результат недели по плану:** Runbook и бэкапы
