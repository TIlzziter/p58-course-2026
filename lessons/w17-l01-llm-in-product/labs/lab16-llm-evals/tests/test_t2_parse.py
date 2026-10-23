import pytest
from parse import parse_answer


def test_plain():
    h = parse_answer('{"hint": "Посмотри на углы", "confidence": 0.8}')
    assert h.hint == "Посмотри на углы" and h.confidence == 0.8


def test_with_text_around():
    h = parse_answer('Конечно! Вот ответ: {"hint": "ход в центр", "confidence": 1} Удачи!')
    assert h.hint == "ход в центр"


def test_fence():
    text = 'Ответ:\n```json\n{"hint": "a", "confidence": 0.5}\n```\nи ещё {"hint": "b", "confidence": 0.1}'
    assert parse_answer(text).hint == "a"


@pytest.mark.parametrize("text", [
    "нет json", "{оборвано", '{"hint": "", "confidence": 0.5}', '{"hint": "x", "confidence": 1.5}',
    '{"hint": "' + "x" * 201 + '", "confidence": 0.5}', '{"confidence": 0.5}', "[1, 2]", "} перепутано {",
    '```json\n[1]\n```',
])
def test_bad(text):
    assert parse_answer(text) is None
