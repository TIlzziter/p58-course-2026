"""Контест 12 · E5*: предохранитель (circuit breaker)."""


class CircuitBreaker:
    """closed: пропускаем; threshold неудач подряд → open на cooldown секунд (отказываем сразу).
    Спустя cooldown — half_open: пропускаем ОДИН пробный запрос, остальные отказываем, пока нет его итога;
    удача → closed (счётчик сброшен), неудача → снова open с этого момента."""

    def __init__(self, threshold: int = 3, cooldown: float = 10.0):
        self.threshold, self.cooldown = threshold, cooldown
        self.state, self.fails, self.opened_at, self.trial = "closed", 0, 0.0, False

    def allow(self, now: float) -> bool:
        if self.state == "open" and now - self.opened_at >= self.cooldown:
            self.state, self.trial = "half_open", False
        if self.state == "closed":
            return True
        if self.state == "half_open" and not self.trial:
            self.trial = True
            return True
        return False

    def record(self, ok: bool, now: float) -> None:
        if self.state == "half_open":
            if ok:
                self.state, self.fails = "closed", 0
            else:
                self.state, self.opened_at = "open", now
            self.trial = False
            return
        if ok:
            self.fails = 0
        else:
            self.fails += 1
            if self.fails >= self.threshold:
                self.state, self.opened_at = "open", now


def run(events: list[tuple[float, bool]], threshold: int = 3, cooldown: float = 10.0) -> str:
    """События (время, ответил бы сервис успешно) по порядку. Для каждого: "-" — отказано без вызова,
    "+" — вызвали и успех, "x" — вызвали и неудача. Итог — строка."""
    cb, out = CircuitBreaker(threshold, cooldown), []
    for t, ok in events:
        if not cb.allow(t):
            out.append("-")
            continue
        cb.record(ok, t)
        out.append("+" if ok else "x")
    return "".join(out)
