import pytest
from game.repo import Base, MatchRepo
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


@pytest.fixture
def repo():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        yield MatchRepo(s)


def test_add(repo):
    assert repo.add("A", "ann", 7, 100) == 1
