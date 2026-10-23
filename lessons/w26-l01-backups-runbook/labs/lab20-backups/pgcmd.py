"""Задача 5. Команды pg_dump / pg_restore для настоящего PostgreSQL проекта."""
from urllib.parse import unquote, urlsplit  # noqa: F401


def parse_dsn(url: str) -> dict:
    """postgresql[+драйвер]://user:password@host[:port]/db → {"user", "password", "host", "port", "db"}.
    Порт по умолчанию 5432 (int). Логин и пароль раскодировать (%40 → @). Не postgresql — ValueError."""
    raise NotImplementedError("TODO")


def pg_dump_cmd(url: str, out_file: str) -> tuple[list[str], dict]:
    """Аргументы и переменные окружения для pg_dump в формате custom. Пароль — только в env PGPASSWORD,
    никогда в аргументах (их видно в ps)."""
    raise NotImplementedError("TODO")


def pg_restore_cmd(url: str, dump_file: str, jobs: int = 2) -> tuple[list[str], dict]:
    """pg_restore в существующую базу: --clean --if-exists --no-owner, параллельно -j jobs."""
    raise NotImplementedError("TODO")


def compose_exec(service: str, argv: list[str], env: dict) -> list[str]:
    """Обернуть команду для запуска внутри контейнера: docker compose exec -T -e K=V … service argv."""
    raise NotImplementedError("TODO")
