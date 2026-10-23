"""Задачи 5–6. Правило алерта и уведомления без спама."""


def evaluate(samples: list[tuple[float, float]], threshold: float, for_s: float) -> list[tuple[float, str]]:
    """События алерта «значение > threshold непрерывно не меньше for_s секунд»: (ts, "firing") и (ts, "resolved")."""
    events = []
    for ts, v in samples:
        if v > threshold:
            events.append((ts, "firing"))
        else:
            events.append((ts, "resolved"))
    return events


class Notifier:
    """Сообщения в Telegram (parse_mode=HTML) по набору горящих алертов. Формат — в README."""

    def __init__(self, repeat_s: float = 3600):
        self.repeat_s = repeat_s

    def process(self, ts: float, firing: set[str]) -> list[str]:
        return [f"🔴 <b>{k}</b>" for k in firing]
