import pytest
from db import make_engine
from models import Base
from sqlalchemy.ext.asyncio import async_sessionmaker


@pytest.fixture
async def engine(tmp_path):
    eng = make_engine(f"sqlite+aiosqlite:///{tmp_path / 'test.db'}")
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest.fixture
def sessions(engine):
    return async_sessionmaker(engine, expire_on_commit=False)


@pytest.fixture
async def session(sessions):
    async with sessions() as s:
        yield s


@pytest.fixture
async def players(session):
    """Четыре игрока в базе: tg_id 1..4 — Аня, Боря, Вика, Гоша."""
    import repo
    for tg, name in [(1, "Аня"), (2, "Боря"), (3, "Вика"), (4, "Гоша")]:
        await repo.get_or_create_player(session, tg, name)
    await session.commit()
