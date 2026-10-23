"""Окружение Alembic (готово): берёт URL из DATABASE_URL и метаданные моделей для autogenerate."""
import os

from alembic import context
from sqlalchemy import create_engine

from db import sync_url
from models import Base

config = context.config
target_metadata = Base.metadata


def url() -> str:
    return sync_url(config.get_main_option("sqlalchemy.url") or os.environ.get("DATABASE_URL", "sqlite:///rating.db"))


def run_migrations_offline() -> None:
    context.configure(url=url(), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_engine(url())
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata,
                          render_as_batch=connection.dialect.name == "sqlite")
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
