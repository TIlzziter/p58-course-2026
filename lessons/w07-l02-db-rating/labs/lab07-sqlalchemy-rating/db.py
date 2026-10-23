"""Подключение к базе (готово). Один и тот же код работает с SQLite и PostgreSQL — меняется только URL.

    sqlite+aiosqlite:///rating.db                          — файл рядом, для разработки и тестов
    postgresql+asyncpg://game:secret@db:5432/game          — PostgreSQL из docker compose
"""
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


def make_engine(url: str, echo: bool = False) -> AsyncEngine:
    engine = create_async_engine(url, echo=echo)
    if url.startswith("sqlite"):
        # SQLite по умолчанию НЕ проверяет внешние ключи — включаем на каждом соединении.
        @event.listens_for(engine.sync_engine, "connect")
        def _fk_on(dbapi_conn, _record):
            cur = dbapi_conn.cursor()
            cur.execute("PRAGMA foreign_keys=ON")
            cur.close()
    return engine


def sync_url(url: str) -> str:
    """URL для Alembic: миграции запускаем синхронным драйвером."""
    return url.replace("+aiosqlite", "").replace("+asyncpg", "+psycopg")
