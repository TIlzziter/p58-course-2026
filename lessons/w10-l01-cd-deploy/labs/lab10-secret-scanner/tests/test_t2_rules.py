import pytest
from fakes import AWS, GH, PEM, TG

from scanner import scan_line


@pytest.mark.parametrize("line, rule, value", [
    (f"BOT_TOKEN={TG}", "telegram_bot_token", TG),
    (f'bot = Bot("{TG}")', "telegram_bot_token", TG),
    (f"export GH={GH}", "github_token", GH),
    (f"aws_access_key_id = {AWS}", "aws_access_key", AWS),
    (PEM, "private_key", PEM),
    ("DATABASE_URL=postgresql://game:S3cr3t-Pa55@db:5432/game", "url_password", "S3cr3t-Pa55"),
])
def test_known_rules(line, rule, value):
    assert scan_line(line) == [(rule, value)]


@pytest.mark.parametrize("line, value", [
    ('password = "hunter2hunter2"', "hunter2hunter2"),
    ("POSTGRES_PASSWORD: s3cretpass", "s3cretpass"),
    ('SECRET_KEY = "a8f5f167f44f4964e6c998dee827110c"', "a8f5f167f44f4964e6c998dee827110c"),
    ("jwt_secret: 9f8e7d6c5b4a3210ffee", "9f8e7d6c5b4a3210ffee"),
])
def test_generic(line, value):
    assert scan_line(line) == [("generic_assignment", value)]


@pytest.mark.parametrize("line", [
    "API_KEY=changeme", "BOT_TOKEN=your_token_here", "password = <пароль>", "TOKEN=${BOT_TOKEN}",
    "token: ${{ secrets.T }}", 'password = os.getenv("DB_PASSWORD")', "SECRET=xxxxxxxx", "MAX_TOKENS=4096",
    "TOKEN=abc", "page_token = next_page", "POSTGRES_PASSWORD: game", "url = 'https://example.org/a@b'",
])
def test_no_false_positives(line):
    assert scan_line(line) == []


def test_specific_rule_wins_over_generic():
    # токен Telegram в присваивании — одно замечание, а не два
    assert scan_line(f"BOT_TOKEN = '{TG}'") == [("telegram_bot_token", TG)]


def test_ignore_mark():
    assert scan_line(f"BOT_TOKEN={TG}  # secret-scan: ignore") == []


def test_two_on_one_line():
    assert [r for r, _ in scan_line(f"{GH} {AWS}")] == ["github_token", "aws_access_key"]
