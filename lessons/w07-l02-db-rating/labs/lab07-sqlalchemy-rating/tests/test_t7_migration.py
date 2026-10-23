from pathlib import Path

from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, inspect

from models import Base

HERE = Path(__file__).resolve().parent.parent


def cfg(url):
    c = Config(str(HERE / "alembic.ini"))
    c.set_main_option("sqlalchemy.url", url)
    return c


def test_upgrade_matches_models(tmp_path):
    url = f"sqlite:///{tmp_path / 'm.db'}"
    command.upgrade(cfg(url), "head")
    engine = create_engine(url)
    with engine.connect() as conn:
        diff = compare_metadata(MigrationContext.configure(conn), Base.metadata)
    engine.dispose()
    assert diff == [], f"миграция не совпадает с моделями: {diff}"


def test_downgrade_removes_everything(tmp_path):
    url = f"sqlite:///{tmp_path / 'm.db'}"
    command.upgrade(cfg(url), "head")
    command.downgrade(cfg(url), "base")
    engine = create_engine(url)
    tables = set(inspect(engine).get_table_names()) - {"alembic_version"}
    engine.dispose()
    assert tables == set()


def test_upgrade_again(tmp_path):
    url = f"sqlite:///{tmp_path / 'm.db'}"
    for target in ("head", "base", "head"):
        (command.upgrade if target == "head" else command.downgrade)(cfg(url), target)
