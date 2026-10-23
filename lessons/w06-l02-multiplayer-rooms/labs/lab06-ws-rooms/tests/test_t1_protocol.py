import json

import pytest
from protocol import ProtocolError, parse_message


@pytest.mark.parametrize("raw,exp", [
    ('{"type": "move", "col": 3}', {"type": "move", "col": 3}),
    ('{"type": "move", "col": 0}', {"type": "move", "col": 0}),
    ('{"type": "chat", "text": "  привет  "}', {"type": "chat", "text": "привет"}),
    ('{"type": "ping"}', {"type": "ping"}),
])
def test_ok(raw, exp):
    assert parse_message(raw) == exp


@pytest.mark.parametrize("raw,code", [
    ("not json", "bad_json"),
    ("", "bad_json"),
    ("[1, 2]", "bad_type"),
    ('"move"', "bad_type"),
    ('{"col": 3}', "bad_type"),
    ('{"type": "jump"}', "bad_type"),
    ('{"type": "move"}', "bad_field"),
    ('{"type": "move", "col": "3"}', "bad_field"),
    ('{"type": "move", "col": true}', "bad_field"),
    ('{"type": "move", "col": 7}', "bad_field"),
    ('{"type": "move", "col": -1}', "bad_field"),
    ('{"type": "move", "col": 3.0}', "bad_field"),
    ('{"type": "move", "col": 3, "player": 2}', "bad_field"),
    ('{"type": "chat", "text": "   "}', "bad_field"),
    ('{"type": "chat", "text": 5}', "bad_field"),
    ('{"type": "ping", "x": 1}', "bad_field"),
])
def test_errors(raw, code):
    with pytest.raises(ProtocolError) as e:
        parse_message(raw)
    assert e.value.code == code


def test_chat_limit():
    assert parse_message(json.dumps({"type": "chat", "text": "я" * 200}))["text"] == "я" * 200
    with pytest.raises(ProtocolError):
        parse_message(json.dumps({"type": "chat", "text": "я" * 201}))
