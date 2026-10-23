import pytest
from client import BudgetExceeded, LLMClient, LLMError

MSG = [{"role": "user", "content": "hi"}]


class Script:
    """Подменный transport: отдаёт ответы по списку; Exception в списке — бросает его."""

    def __init__(self, *replies):
        self.replies = list(replies)
        self.seen = []

    def __call__(self, messages):
        self.seen.append(messages)
        r = self.replies.pop(0)
        if isinstance(r, Exception):
            raise r
        return r


def ok(text="ответ", tin=10, tout=5):
    return {"status": 200, "text": text, "usage": {"in": tin, "out": tout}}


def err(status, retry_after=None):
    return {"status": status, "text": "", "usage": {"in": 0, "out": 0}, "retry_after": retry_after}


def test_success_and_usage():
    c = LLMClient(Script(ok()), sleep=lambda s: None)
    assert c.complete(MSG) == "ответ"
    assert c.spent == 15 and c.calls == 1


def test_retries_with_backoff():
    pauses = []
    t = Script(err(503), TimeoutError(), err(429), ok("наконец"))
    c = LLMClient(t, sleep=pauses.append, max_retries=3, base_delay=0.5)
    assert c.complete(MSG) == "наконец"
    assert pauses == [0.5, 1.0, 2.0] and c.calls == 4


def test_retry_after_header():
    pauses = []
    c = LLMClient(Script(err(429, retry_after=7), ok()), sleep=pauses.append)
    c.complete(MSG)
    assert pauses == [7]


def test_give_up():
    pauses = []
    c = LLMClient(Script(err(500), err(500), err(500)), sleep=pauses.append, max_retries=2)
    with pytest.raises(LLMError):
        c.complete(MSG)
    assert c.calls == 3 and pauses == [0.5, 1.0]          # после последней попытки не спим


def test_no_retry_on_400():
    c = LLMClient(Script(err(400), ok()), sleep=lambda s: None)
    with pytest.raises(LLMError):
        c.complete(MSG)
    assert c.calls == 1


def test_cache():
    t = Script(ok("раз"), ok("два"))
    c = LLMClient(t, sleep=lambda s: None)
    assert c.complete(MSG) == "раз"
    assert c.complete([{"content": "hi", "role": "user"}]) == "раз"   # тот же запрос, другой порядок ключей
    assert c.calls == 1 and c.spent == 15
    assert c.complete(MSG + [{"role": "user", "content": "ещё"}]) == "два"


def test_budget():
    c = LLMClient(Script(ok(tin=60, tout=40), ok()), sleep=lambda s: None, budget=100)
    c.complete(MSG)
    assert c.complete(MSG) == "ответ"                        # из кэша — можно
    with pytest.raises(BudgetExceeded):
        c.complete([{"role": "user", "content": "новый"}])
    assert issubclass(BudgetExceeded, LLMError)
