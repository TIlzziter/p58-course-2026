from alerts import Notifier


def test_new_repeat_resolve():
    n = Notifier(repeat_s=600)
    assert n.process(0, {"high_5xx"}) == ["🔴 <b>high_5xx</b>"]
    assert n.process(60, {"high_5xx"}) == []                         # без спама
    assert n.process(600, {"high_5xx"}) == ["🔁 <b>high_5xx</b> — всё ещё горит"]
    assert n.process(700, {"high_5xx"}) == []
    assert n.process(800, set()) == ["✅ <b>high_5xx</b> — решено"]
    assert n.process(900, set()) == []


def test_order_and_many():
    n = Notifier(repeat_s=100)
    n.process(0, {"b", "a"})
    assert n.process(100, {"a", "c"}) == ["🔴 <b>c</b>", "🔁 <b>a</b> — всё ещё горит", "✅ <b>b</b> — решено"]


def test_html_escaped():
    n = Notifier()
    assert n.process(0, {"latency<p95>&co"}) == ["🔴 <b>latency&lt;p95&gt;&amp;co</b>"]


def test_refire_after_resolve():
    n = Notifier(repeat_s=1000)
    n.process(0, {"x"})
    n.process(10, set())
    assert n.process(20, {"x"}) == ["🔴 <b>x</b>"]
