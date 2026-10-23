import pytest
from demo import make_demo_db


@pytest.fixture
def db(tmp_path):
    return make_demo_db(tmp_path / "game.db")
