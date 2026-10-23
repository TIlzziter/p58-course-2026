"""Задачи 3–4. Сервер — источник истины: проверяем то, что прислал клиент."""
import math  # noqa: F401
import statistics  # noqa: F401


class MoveValidator:
    """Проверка ходов в игре на поле width × height, где игрок двигается не быстрее max_speed клеток в секунду.

    check(player, ts, x, y) -> None, если ход принят, иначе причина:
      "out_of_bounds" — точка вне поля (0 <= x < width, 0 <= y < height; координаты дробные);
      "stale"         — ts не больше времени последнего принятого хода этого игрока (повтор, старый пакет);
      "too_fast"      — расстояние от последней принятой точки / время > max_speed * (1 + tolerance).
    Проверки в этом порядке. Первый ход игрока — только проверка поля. Отклонённый ход состояние не меняет.
    """

    def __init__(self, width: float, height: float, max_speed: float, tolerance: float = 0.1):
        self.width, self.height = width, height
        self.max_speed = max_speed
        self.tolerance = tolerance
        self.last: dict[str, tuple[float, float, float]] = {}

    def check(self, player: str, ts: float, x: float, y: float) -> str | None:
        # Сейчас сервер верит клиенту во всём. TODO: проверки из docstring
        self.last[player] = (ts, x, y)
        return None


def click_audit(times_ms: list[int], claimed: int, max_cps: int = 15, min_jitter_ms: float = 3) -> list[str]:
    """Проверка сессии кликера: времена нажатий (мс, от сервера) и счёт, который прислал клиент.

    Если времена не по неубыванию — сразу ["unsorted"]. Иначе причины в таком порядке:
      "count_mismatch" — claimed не равен числу нажатий;
      "too_fast"       — в каком-то окне [t, t + 1000) больше max_cps нажатий;
      "robotic"        — нажатий не меньше 10, а стандартное отклонение интервалов (statistics.pstdev)
                         меньше min_jitter_ms: человек так ровно не кликает.
    Честная сессия — [].
    """
    raise NotImplementedError
