import pytest


class FakeClock:
    """Подменные часы: время двигаем руками, тесты не ждут."""

    def __init__(self, t: float = 1000.0):
        self.t = t

    def __call__(self) -> float:
        return self.t

    def tick(self, dt: float) -> None:
        self.t += dt


@pytest.fixture
def clock():
    return FakeClock()
