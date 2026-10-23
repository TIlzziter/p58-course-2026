"""Задачи 3–4. Сервер — источник истины: проверяем то, что прислал клиент."""
import math
import statistics


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
        if not (0 <= x < self.width and 0 <= y < self.height):
            return "out_of_bounds"
        prev = self.last.get(player)
        if prev is not None:
            pts, px, py = prev
            if ts <= pts:
                return "stale"
            if math.hypot(x - px, y - py) / (ts - pts) > self.max_speed * (1 + self.tolerance):
                return "too_fast"
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
    if any(b < a for a, b in zip(times_ms, times_ms[1:])):
        return ["unsorted"]
    reasons = []
    if claimed != len(times_ms):
        reasons.append("count_mismatch")
    j = 0
    for i, t in enumerate(times_ms):
        while times_ms[j] <= t - 1000:
            j += 1
        if i - j + 1 > max_cps:
            reasons.append("too_fast")
            break
    if len(times_ms) >= 10:
        gaps = [b - a for a, b in zip(times_ms, times_ms[1:])]
        if statistics.pstdev(gaps) < min_jitter_ms:
            reasons.append("robotic")
    return reasons
