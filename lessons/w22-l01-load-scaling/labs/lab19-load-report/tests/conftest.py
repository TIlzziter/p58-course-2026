from pathlib import Path

import pytest

DATA = Path(__file__).resolve().parent.parent / "data"

SMALL = """ts,name,status,ms
0.5,GET /a,200,10
0.0,GET /a,200,30
1.0,GET /b,500,100
2.0,GET /a,200,20
bad,GET /a,200,10
3.0,GET /b,200,50
3.5,GET /a,0,40
4.0,GET /a,200,abc
4.0,,200,5
"""


@pytest.fixture
def small_csv(tmp_path):
    p = tmp_path / "small.csv"
    p.write_text(SMALL, encoding="utf-8")
    return p


@pytest.fixture
def before_path():
    return DATA / "before.csv"


@pytest.fixture
def after_path():
    return DATA / "after.csv"
