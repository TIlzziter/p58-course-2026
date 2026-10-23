import pytest

from conftest import ex
from review import start_order


def test_good_order():
    assert start_order(ex("compose.good.yml")) == ["db", "app", "bot", "nginx"]


def test_alphabetical_tie():
    text = "services:\n  web: {}\n  api: {}\n  cache: {}\n"
    assert start_order(text) == ["api", "cache", "web"]


def test_unknown_dependency_ignored():
    assert start_order(ex("compose.agent.yml")) == ["db", "app", "bot", "nginx"]


def test_cycle():
    text = "services:\n  a: {depends_on: [b]}\n  b: {depends_on: [a]}\n  c: {}\n"
    with pytest.raises(ValueError):
        start_order(text)
