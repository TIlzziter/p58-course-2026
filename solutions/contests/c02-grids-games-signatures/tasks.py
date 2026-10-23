"""Контест 2 — эталонные решения задач A–D."""
import hashlib
import hmac
from urllib.parse import unquote_plus


# ---------- A. Сетки ----------
def column(board: list[list[int]], c: int) -> list[int]:
    """A1. Столбец c снизу вверх, без пустых (0) клеток."""
    return [row[c] for row in reversed(board) if row[c] != 0]


def gravity(board: list[list[int]]) -> list[list[int]]:
    """A2. Все фишки падают вниз своего столбца, порядок в столбце сохраняется. Новое поле."""
    rows, cols = len(board), len(board[0])
    out = [[0] * cols for _ in range(rows)]
    for c in range(cols):
        stack = column(board, c)                 # снизу вверх
        for i, v in enumerate(stack):
            out[rows - 1 - i][c] = v
    return out


def longest_run(board: list[list[int]], p: int) -> int:
    """A3. Самая длинная непрерывная горизонтальная или вертикальная линия фишек игрока p."""
    best = 0
    lines = [list(r) for r in board] + [list(col) for col in zip(*board)]
    for line in lines:
        cur = 0
        for v in line:
            cur = cur + 1 if v == p else 0
            best = max(best, cur)
    return best


# ---------- B. Игры ----------
def k_in_row(board: list[str], k: int) -> str | None:
    """B1. Поле n×n строками из "XO.", победитель — k одинаковых подряд по любой линии. Нет — None."""
    n = len(board)
    for r in range(n):
        for c in range(n):
            ch = board[r][c]
            if ch == ".":
                continue
            for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
                if all(0 <= r + i * dr < n and 0 <= c + i * dc < n and board[r + i * dr][c + i * dc] == ch
                       for i in range(k)):
                    return ch
    return None


def next_turn(board: str) -> str:
    """B2. Крестики-нолики, X ходит первым. Чей ход: "X", "O" или "invalid", если счёт фишек невозможен."""
    x, o = board.count("X"), board.count("O")
    if x == o:
        return "X"
    if x == o + 1:
        return "O"
    return "invalid"


def click_to_cell(x: float, y: float, css_w: float, css_h: float, rows: int, cols: int) -> tuple[int, int] | None:
    """B3. Клик по canvas в CSS-пикселях (canvas растянут на css_w×css_h) → (строка, столбец) или None вне поля."""
    if not (0 <= x < css_w and 0 <= y < css_h):
        return None
    return int(y * rows // css_h), int(x * cols // css_w)


def _drop(board, c, p):
    for r in range(len(board) - 1, -1, -1):
        if board[r][c] == 0:
            b = [row[:] for row in board]
            b[r][c] = p
            return b
    return None


def _wins(board, p):
    rows, cols = len(board), len(board[0])
    for r in range(rows):
        for c in range(cols):
            for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
                if all(0 <= r + i * dr < rows and 0 <= c + i * dc < cols and board[r + i * dr][c + i * dc] == p
                       for i in range(4)):
                    return True
    return False


def best_drop(board: list[list[int]], p: int) -> int | None:
    """B4*. «4 в ряд»: выигрывающий столбец; иначе столбец, закрывающий выигрыш соперника; иначе ближайший к центру
    свободный (при равенстве — левый). Полное поле — None."""
    cols = len(board[0])
    free = [c for c in range(cols) if board[0][c] == 0]
    if not free:
        return None
    for who in (p, 3 - p):
        for c in free:
            if _wins(_drop(board, c, who), who):
                return c
    center = (cols - 1) / 2
    return min(free, key=lambda c: (abs(c - center), c))


# ---------- C. Подписи ----------
def parse_query(qs: str) -> dict[str, str]:
    """C1. Строка запроса → словарь без urllib.parse_qs: '+' — пробел, %XX — байты UTF-8. Без '=' — пустое значение."""
    out = {}
    for part in qs.split("&"):
        if not part:
            continue
        k, _, v = part.partition("=")
        out[unquote_plus(k)] = unquote_plus(v)
    return out


def sign(message: str, key: str) -> str:
    """C2. HMAC-SHA256 в hex."""
    return hmac.new(key.encode(), message.encode(), hashlib.sha256).hexdigest()


def forged(items: list[tuple[str, str]], key: str) -> list[int]:
    """C2 (продолжение). Индексы пар (сообщение, подпись), где подпись неверна."""
    return [i for i, (m, s) in enumerate(items) if not hmac.compare_digest(sign(m, key), s.lower())]


def fresh(auth_dates: list[int], now: int, max_age: int) -> int:
    """C3. Сколько отметок времени свежие: не из будущего и не старше max_age секунд."""
    return sum(1 for t in auth_dates if 0 <= now - t <= max_age)


# ---------- D. Docker ----------
def parse_port(spec: str) -> dict:
    """D1. Строка ports из compose → {"ip", "host", "container", "proto"}."""
    proto = "tcp"
    if "/" in spec:
        spec, proto = spec.split("/")
    parts = spec.split(":")
    if len(parts) == 1:
        return {"ip": None, "host": None, "container": int(parts[0]), "proto": proto}
    if len(parts) == 2:
        return {"ip": "0.0.0.0", "host": int(parts[0]), "container": int(parts[1]), "proto": proto}
    return {"ip": parts[0], "host": int(parts[1]), "container": int(parts[2]), "proto": proto}


def parse_image(ref: str) -> tuple[str, str, str]:
    """D2. Ссылка на образ → (реестр, имя, тег). По умолчанию docker.io и latest; официальные — library/."""
    registry = "docker.io"
    rest = ref
    first, sep, tail = ref.partition("/")
    if sep and ("." in first or ":" in first or first == "localhost"):
        registry, rest = first, tail
    if "@" in rest:
        rest = rest.split("@")[0]
    name, tag = rest, "latest"
    last = rest.rsplit("/", 1)[-1]
    if ":" in last:
        name, tag = rest.rsplit(":", 1)
    if registry == "docker.io" and "/" not in name:
        name = "library/" + name
    return registry, name, tag


def parse_env(text: str) -> dict[str, str]:
    """D3. Файл .env → словарь: комментарии, пустые строки, export, кавычки, # после значения без кавычек."""
    out = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        k, sep, v = line.partition("=")
        if not sep:
            continue
        v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1]
        else:
            v = v.split(" #")[0].strip()
        out[k.strip()] = v
    return out
