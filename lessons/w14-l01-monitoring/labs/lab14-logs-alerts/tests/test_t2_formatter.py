import json
import logging

import pytest
from logs import JsonFormatter


@pytest.fixture
def log():
    records = []

    class H(logging.Handler):
        def emit(self, record):
            records.append(self.format(record))

    h = H()
    h.setFormatter(JsonFormatter())
    logger = logging.getLogger("game.test")
    logger.handlers[:] = [h]
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    return logger, records


def test_basic(log):
    logger, out = log
    logger.info("игрок %s вошёл", "ann")
    rec = json.loads(out[0])
    assert list(rec) == ["ts", "level", "logger", "msg"]
    assert rec["level"] == "INFO" and rec["logger"] == "game.test" and rec["msg"] == "игрок ann вошёл"
    assert rec["ts"].endswith("+00:00") and len(rec["ts"]) == len("2027-02-09T10:00:00.123+00:00")
    assert "игрок" in out[0]                      # без \u-экранирования


def test_extra_sorted(log):
    logger, out = log
    logger.warning("slow tick", extra={"room": "R1", "ms": 180, "players": ["a", "b"]})
    rec = json.loads(out[0])
    assert list(rec)[4:] == ["ms", "players", "room"]
    assert rec["ms"] == 180 and rec["players"] == ["a", "b"]


def test_exception(log):
    logger, out = log
    try:
        raise ValueError("плохой ход")
    except ValueError:
        logger.exception("ход отклонён", extra={"room": "R2"})
    rec = json.loads(out[0])
    assert rec["level"] == "ERROR" and rec["exc"] == "ValueError: плохой ход"
    assert list(rec)[-1] == "exc" and "\n" not in out[0]


def test_non_json_extra(log):
    logger, out = log
    logger.info("x", extra={"obj": object()})
    assert json.loads(out[0])["obj"].startswith("<object object")
