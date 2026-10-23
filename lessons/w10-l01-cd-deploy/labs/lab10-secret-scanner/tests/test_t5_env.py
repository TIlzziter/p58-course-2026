import pytest

from scanner import check_env, parse_env

TEXT = """
# Telegram
BOT_TOKEN=123:abc
export WEBAPP_URL=https://game.example.org/app?x=1
DATABASE_URL = "postgresql://game:pa ss@db/game"
EMPTY=
QUOTED='a # не комментарий'
DEBUG=1  # комментарий после значения
"""


def test_parse():
    assert parse_env(TEXT) == {
        "BOT_TOKEN": "123:abc",
        "WEBAPP_URL": "https://game.example.org/app?x=1",
        "DATABASE_URL": "postgresql://game:pa ss@db/game",
        "EMPTY": "",
        "QUOTED": "a # не комментарий",
        "DEBUG": "1",
    }


def test_last_wins():
    assert parse_env("A=1\nA=2\n") == {"A": "2"}


@pytest.mark.parametrize("text, line", [("A=1\nэто не строка\n", 2), ("1A=2", 1), ('A="без конца', 1)])
def test_errors(text, line):
    with pytest.raises(ValueError, match=f"строка {line}"):
        parse_env(text)


def test_check_env():
    example = "BOT_TOKEN=\nDATABASE_URL=\nREDIS_URL=redis://redis:6379\n"
    actual = "BOT_TOKEN=123:abc\nREDIS_URL=\nDEBUG=1\n"
    assert check_env(example, actual) == {"missing": ["DATABASE_URL"], "extra": ["DEBUG"], "empty": ["REDIS_URL"]}
