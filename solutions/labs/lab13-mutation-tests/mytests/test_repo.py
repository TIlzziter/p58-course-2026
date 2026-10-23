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
    engine.dispose()


@pytest.fixture
def filled(repo):
    for room, winner, score, ts in [("A", "bob", 10, 100), ("A", "ann", 7, 200), ("B", "bob", 3, 150),
                                    ("A", "cat", 9, 300), ("B", "ann", 5, 300), ("A", "dan", 1, 300)]:
        repo.add(room, winner, score, ts)
    return repo


def test_add_returns_ids(repo):
    assert repo.add("A", "ann", 1, 1) == 1 and repo.add("A", "ann", 1, 2) == 2


def test_top(filled):
    assert filled.top_winners(2) == [("ann", 2), ("bob", 2)]
    assert filled.top_winners(10) == [("ann", 2), ("bob", 2), ("cat", 1), ("dan", 1)]
    assert filled.top_winners(1) == [("ann", 1 + 1)]


def test_history(filled):
    assert filled.history("A") == [("dan", 1), ("cat", 9), ("ann", 7), ("bob", 10)]    # 300, 300 (позже добавлен), 200, 100
    assert filled.history("A", limit=2) == [("dan", 1), ("cat", 9)]
    assert filled.history("Z") == []


def test_delete_older(filled):
    assert filled.delete_older(150) == 1           # только ts=100; ровно 150 остаётся
    assert filled.history("B") == [("ann", 5), ("bob", 3)]
    assert filled.delete_older(1000) == 5 and filled.top_winners(5) == []
