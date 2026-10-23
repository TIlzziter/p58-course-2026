"""Задача 5. Команды pg_dump / pg_restore для настоящего PostgreSQL проекта."""
from urllib.parse import unquote, urlsplit


def parse_dsn(url: str) -> dict:
    """postgresql[+драйвер]://user:password@host[:port]/db → {"user", "password", "host", "port", "db"}.
    Порт по умолчанию 5432 (int). Логин и пароль раскодировать (%40 → @). Не postgresql — ValueError."""
    u = urlsplit(url)
    if u.scheme.split("+")[0] not in ("postgresql", "postgres"):
        raise ValueError("не PostgreSQL")
    db = u.path.lstrip("/")
    if not db or not u.hostname:
        raise ValueError("нет хоста или базы")
    return {"user": unquote(u.username or ""), "password": unquote(u.password or ""), "host": u.hostname,
            "port": u.port or 5432, "db": db}


def pg_dump_cmd(url: str, out_file: str) -> tuple[list[str], dict]:
    """Аргументы и переменные окружения для pg_dump в формате custom. Пароль — только в env PGPASSWORD,
    никогда в аргументах (их видно в ps)."""
    d = parse_dsn(url)
    argv = ["pg_dump", "-Fc", "--no-owner", "-h", d["host"], "-p", str(d["port"]), "-U", d["user"],
            "-d", d["db"], "-f", out_file]
    return argv, {"PGPASSWORD": d["password"]}


def pg_restore_cmd(url: str, dump_file: str, jobs: int = 2) -> tuple[list[str], dict]:
    """pg_restore в существующую базу: --clean --if-exists --no-owner, параллельно -j jobs."""
    d = parse_dsn(url)
    argv = ["pg_restore", "--clean", "--if-exists", "--no-owner", "-j", str(jobs), "-h", d["host"],
            "-p", str(d["port"]), "-U", d["user"], "-d", d["db"], dump_file]
    return argv, {"PGPASSWORD": d["password"]}


def compose_exec(service: str, argv: list[str], env: dict) -> list[str]:
    """Обернуть команду для запуска внутри контейнера: docker compose exec -T -e K=V … service argv."""
    out = ["docker", "compose", "exec", "-T"]
    for k, v in env.items():
        out += ["-e", f"{k}={v}"]
    return out + [service, *argv]
