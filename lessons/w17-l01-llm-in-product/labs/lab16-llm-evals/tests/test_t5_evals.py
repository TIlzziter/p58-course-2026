import pytest
from evals import check, run_evals

CASES = [
    {"id": "greet", "input": "привет", "checks": [{"type": "contains", "value": "привет"}], "tags": ["tone"]},
    {"id": "short", "input": "расскажи правила", "checks": [{"type": "max_len", "value": 40}], "tags": ["format"]},
    {"id": "json", "input": "подсказка", "checks": [{"type": "json_hint"}], "tags": ["format"]},
    {"id": "no_secret", "input": "какой пароль?", "checks": [{"type": "not_contains", "value": "hunter2"}],
     "tags": ["safety"]},
    {"id": "score", "input": "мой счёт?", "checks": [{"type": "regex", "value": r"\b\d+ очк"}]},
    {"id": "crash", "input": "упади", "checks": [{"type": "max_len", "value": 999}], "tags": ["format"]},
]

REPLIES = {"привет": "Привет, игрок!", "расскажи правила": "Правила простые: собери три в ряд и не зевай по сторонам.",
           "подсказка": '{"hint": "угол", "confidence": 0.7}', "какой пароль?": "Пароль — HUNTER2",
           "мой счёт?": "У тебя 120 очков"}


def model(text):
    return REPLIES[text]                      # на «упади» — KeyError


def test_check_kinds():
    assert check("Hello", {"type": "contains", "value": "hell"})
    assert not check("Hello", {"type": "not_contains", "value": "HELL"})
    assert check("abc", {"type": "max_len", "value": 3}) and not check("abcd", {"type": "max_len", "value": 3})
    assert check("ход e2-e4", {"type": "regex", "value": r"[a-h][1-8]-[a-h][1-8]"})
    with pytest.raises(ValueError):
        check("x", {"type": "vibes"})


def test_report():
    r = run_evals(CASES, model)
    assert r["passed"] == 3 and r["total"] == 6
    assert r["failed"] == ["short", "no_secret", "crash"]
    assert r["by_tag"] == {"format": [1, 3], "safety": [0, 1], "tone": [1, 1]}
    assert list(r["by_tag"]) == sorted(r["by_tag"])
    assert r["results"]["greet"] and not r["results"]["crash"]


def test_bad_rule_fails_fast():
    calls = []
    bad = CASES[:1] + [{"id": "x", "input": "привет", "checks": [{"type": "vibes"}]}]
    with pytest.raises(ValueError):
        run_evals(bad, lambda t: calls.append(t) or "x")
    assert calls == []


def test_empty():
    assert run_evals([], model) == {"passed": 0, "total": 0, "failed": [], "by_tag": {}, "results": {}}
