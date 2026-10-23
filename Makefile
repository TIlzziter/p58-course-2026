# Сборка и проверка материалов курса. PYTHON можно переопределить: make check PYTHON=.venv/bin/python
PYTHON ?= python3

.PHONY: all decks contests readmes rating check
all: decks contests readmes rating

decks:      ## собрать все презентации .deck → .html
	$(PYTHON) tools/deck.py $(wildcard lessons/*/*.deck)

contests:   ## собрать листы контестов sheet.md → sheet.html + sheet.pdf (нужен Chrome/Chromium)
	$(PYTHON) tools/contest.py $(wildcard contests/*/sheet.md)

readmes:    ## README уроков и таблица расписания в README.md
	$(PYTHON) tools/gen_readmes.py

rating:     ## шаблон таблицы рейтинга
	$(PYTHON) tools/rating.py

check:      ## проверить лабораторные, контесты и уроки
	PYTHON=$(PYTHON) scripts/check_all.sh
