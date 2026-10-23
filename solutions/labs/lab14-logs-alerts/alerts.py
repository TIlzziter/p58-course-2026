"""Задачи 5–6. Правило алерта и уведомления без спама."""
import html


def evaluate(samples: list[tuple[float, float]], threshold: float, for_s: float) -> list[tuple[float, str]]:
    """События алерта «значение > threshold дольше for_s»: (ts, "firing") и (ts, "resolved")."""
    events, since, firing = [], None, False
    for ts, v in samples:
        if v > threshold:
            if since is None:
                since = ts
            if not firing and ts - since >= for_s:
                firing = True
                events.append((ts, "firing"))
        else:
            if firing:
                events.append((ts, "resolved"))
            since, firing = None, False
    return events


class Notifier:
    def __init__(self, repeat_s: float = 3600):
        self.repeat_s = repeat_s
        self.last_sent: dict[str, float] = {}      # горящие и когда последний раз писали

    def process(self, ts: float, firing: set[str]) -> list[str]:
        new = sorted(k for k in firing if k not in self.last_sent)
        again = sorted(k for k in firing if k in self.last_sent and ts - self.last_sent[k] >= self.repeat_s)
        gone = sorted(k for k in self.last_sent if k not in firing)
        msgs = [f"🔴 <b>{html.escape(k)}</b>" for k in new]
        msgs += [f"🔁 <b>{html.escape(k)}</b> — всё ещё горит" for k in again]
        msgs += [f"✅ <b>{html.escape(k)}</b> — решено" for k in gone]
        for k in new + again:
            self.last_sent[k] = ts
        for k in gone:
            del self.last_sent[k]
        return msgs
