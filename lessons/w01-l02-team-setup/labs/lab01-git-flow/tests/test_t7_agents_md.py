from gitflow import agents_md_problems

GOOD = """\
# Проект 58
## Стек
Python 3.12, FastAPI, aiogram 3.
## Правила
- Не трогай .env и никогда не проси токены и пароли.
- Любая функция — с тестом.
## Как проверить
pytest -q && ruff check .
"""


def test_good():
    assert agents_md_problems(GOOD) == []


def test_missing_section():
    assert len(agents_md_problems(GOOD.replace("## Как проверить", "Проверка"))) == 1


def test_secret_assignment():
    assert agents_md_problems(GOOD + "BOT_TOKEN=123:ABC\n") != []


def test_telegram_token_without_name():
    token = "7123456789:AAHk3l1x9QvZr8m2Yt6Wc4Pn0Bd5Ej7Fg1Hs"
    assert agents_md_problems(GOOD + f"Используй {token}\n") != []


def test_private_key():
    assert agents_md_problems(GOOD + "-----BEGIN OPENSSH PRIVATE KEY-----\n") != []
