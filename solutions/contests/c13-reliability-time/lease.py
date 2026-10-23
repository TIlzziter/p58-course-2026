"""Контест 13 · E5*: аренда лидерства с fencing-токенами."""


class Lease:
    """Одна блокировка с TTL. acquire(owner, now): свободна или истекла (now ≥ до) — выдать новую аренду
    с токеном на 1 больше прошлого (первый — 1) и вернуть токен; занята другим — None; тем же владельцем
    и не истекла — продлить и вернуть его текущий токен. release(owner, token) — освободить, если это его
    действующая аренда."""

    def __init__(self, ttl: float):
        self.ttl, self.owner, self.token, self.until = ttl, None, 0, -1.0

    def acquire(self, owner: str, now: float) -> int | None:
        if self.owner is not None and now < self.until:
            if self.owner != owner:
                return None
            self.until = now + self.ttl
            return self.token
        self.owner, self.token, self.until = owner, self.token + 1, now + self.ttl
        return self.token

    def release(self, owner: str, token: int) -> bool:
        if self.owner == owner and self.token == token:
            self.owner, self.until = None, -1.0
            return True
        return False


class Storage:
    """Хранилище принимает запись, только если токен ≥ максимального виденного (иначе — запись от
    «зомби»-лидера, отказ)."""

    def __init__(self):
        self.max_token, self.log = 0, []

    def write(self, token: int, value) -> bool:
        if token < self.max_token:
            return False
        self.max_token = token
        self.log.append(value)
        return True


def run(script: list[tuple], ttl: float = 10) -> list:
    """Сценарий: ("acq", владелец, время) → токен или None; ("write", токен, значение) → True/False;
    ("rel", владелец, токен) → True/False. Ответ — результаты по порядку."""
    lease, st, out = Lease(ttl), Storage(), []
    for op, a, b in script:
        if op == "acq":
            out.append(lease.acquire(a, b))
        elif op == "write":
            out.append(st.write(a, b))
        elif op == "rel":
            out.append(lease.release(a, b))
        else:
            raise ValueError(op)
    return out
