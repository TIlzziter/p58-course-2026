"""Контест 14 · Финал сезона — эталонные решения A1–D3."""
import hashlib
import heapq
import hmac
import re
from urllib.parse import parse_qsl, urlsplit

# ---------- A. Игры ----------

def elo(ra: float, rb: float, score: float, k: float = 32) -> tuple[int, int]:
    """A1. Эло: ожидание A = 1 / (1 + 10^((rb − ra)/400)), score — 1, 0.5 или 0 для A.
    Новые рейтинги, округлить до целых."""
    ea = 1 / (1 + 10 ** ((rb - ra) / 400))
    d = k * (score - ea)
    return round(ra + d), round(rb - d)


def leaderboard(scores: dict[str, int]) -> list[tuple[int, str, int]]:
    """A2. Места «1224»: (место, имя, очки) по убыванию очков, при равенстве — по имени; равные очки —
    равное место, следующее место — пропускает."""
    rows = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
    out, place = [], 0
    for i, (name, s) in enumerate(rows):
        if i == 0 or s != rows[i - 1][1]:
            place = i + 1
        out.append((place, name, s))
    return out


def validate_move(msg) -> list[str]:
    """A3. Сообщение хода по WebSocket: {"type": "move", "room": строка 1–32 символа [a-z0-9-],
    "cell": целое 0–8 (не bool)}, других ключей нет. Ошибки по порядку проверок: "не объект", затем
    для type, room, cell: "<ключ>: нет" или "<ключ>: неверно", затем "лишний ключ: <k>" по алфавиту."""
    if not isinstance(msg, dict):
        return ["не объект"]
    errs = []
    checks = {
        "type": lambda v: v == "move",
        "room": lambda v: isinstance(v, str) and re.fullmatch(r"[a-z0-9-]{1,32}", v) is not None,
        "cell": lambda v: isinstance(v, int) and not isinstance(v, bool) and 0 <= v <= 8,
    }
    for k, ok in checks.items():
        if k not in msg:
            errs.append(f"{k}: нет")
        elif not ok(msg[k]):
            errs.append(f"{k}: неверно")
    errs += [f"лишний ключ: {k}" for k in sorted(set(msg) - set(checks))]
    return errs


def seeding(n: int) -> list[int]:
    """A4*. Посев олимпийской сетки на n = 2^k участников: пары (1, n), … так, чтобы 1 и 2 могли встретиться
    только в финале. Рекурсия: из посева на n/2 каждое s превращается в s, n + 1 − s."""
    if n < 1 or n & (n - 1):
        raise ValueError("нужна степень двойки")
    order = [1]
    while len(order) < n:
        m = len(order) * 2
        order = [x for s in order for x in (s, m + 1 - s)]
    return order


# ---------- B. Сеть ----------

def parse_request(raw: str) -> dict:
    """B1. HTTP/1.1-запрос (строки через \\r\\n): {"method", "path", "query": dict (последнее значение
    побеждает), "headers": имена в нижнем регистре, "body"}. Неверная первая строка — ValueError."""
    head, _, body = raw.partition("\r\n\r\n")
    lines = head.split("\r\n")
    parts = lines[0].split(" ")
    if len(parts) != 3 or not parts[2].startswith("HTTP/"):
        raise ValueError(lines[0])
    u = urlsplit(parts[1])
    headers = {}
    for ln in lines[1:]:
        k, _, v = ln.partition(":")
        headers[k.strip().lower()] = v.strip()
    return {"method": parts[0], "path": u.path, "query": dict(parse_qsl(u.query)), "headers": headers,
            "body": body}


def ws_header(data: bytes) -> dict:
    """B2. Заголовок кадра WebSocket (RFC 6455): FIN — старший бит байта 0, opcode — младшие 4 бита;
    MASK — старший бит байта 1, длина — 7 бит: < 126 — она сама, 126 — следующие 2 байта, 127 — 8 байт
    (big-endian); с маской ещё 4 байта ключа. Ответ {"fin", "opcode", "masked", "length", "header"} —
    header — размер заголовка в байтах. Не хватает байтов — ValueError."""
    if len(data) < 2:
        raise ValueError("коротко")
    fin, opcode = bool(data[0] & 0x80), data[0] & 0x0F
    masked, n = bool(data[1] & 0x80), data[1] & 0x7F
    pos = 2
    if n == 126:
        size = 2
    elif n == 127:
        size = 8
    else:
        size = 0
    if len(data) < pos + size + (4 if masked else 0):
        raise ValueError("коротко")
    if size:
        n = int.from_bytes(data[pos:pos + size], "big")
        pos += size
    if masked:
        pos += 4
    return {"fin": fin, "opcode": opcode, "masked": masked, "length": n, "header": pos}


def sign_init_data(fields: dict[str, str], bot_token: str) -> str:
    """Подписать поля как Telegram (для тестов): та же схема, что в verify_init_data."""
    dcs = "\n".join(f"{k}={v}" for k, v in sorted(fields.items()))
    secret = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    h = hmac.new(secret, dcs.encode(), hashlib.sha256).hexdigest()
    from urllib.parse import urlencode
    return urlencode({**fields, "hash": h})


def verify_init_data(init_data: str, bot_token: str) -> dict | None:
    """B3. Проверка initData Mini App: разобрать как query-строку, убрать hash; строка проверки — пары
    "ключ=значение" по алфавиту ключей через \\n; secret = HMAC-SHA256(ключ "WebAppData", bot_token);
    hash = hex HMAC-SHA256(secret, строка). Совпало (hmac.compare_digest) — поля без hash, иначе None."""
    fields = dict(parse_qsl(init_data, keep_blank_values=True))
    got = fields.pop("hash", None)
    if got is None:
        return None
    dcs = "\n".join(f"{k}={v}" for k, v in sorted(fields.items()))
    secret = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    want = hmac.new(secret, dcs.encode(), hashlib.sha256).hexdigest()
    return fields if hmac.compare_digest(got, want) else None


# ---------- C. Алгоритмы ----------

def swiss_pairs(points: dict[str, float], played: set[frozenset]) -> list[tuple[str, str]]:
    """C1. Швейцарка: игроки по убыванию очков, при равенстве — по имени. Первый свободный играет с
    ближайшим ниже, с кем ещё не играл; если дальше пару не собрать — перебор с возвратом. Чётное число
    игроков; пар нет — ValueError."""
    order = sorted(points, key=lambda p: (-points[p], p))

    def go(rest):
        if not rest:
            return []
        a = rest[0]
        for i in range(1, len(rest)):
            b = rest[i]
            if frozenset((a, b)) in played:
                continue
            tail = go(rest[1:i] + rest[i + 1:])
            if tail is not None:
                return [(a, b), *tail]
        return None

    res = go(order)
    if res is None:
        raise ValueError("пары не собрать")
    return res


def latency(graph: dict[str, dict[str, int]], src: str) -> dict[str, int]:
    """C2. Дейкстра: кратчайшие задержки от src до всех достижимых узлов (рёбра направленные, мс).
    Ответ — по алфавиту узлов."""
    dist = {src: 0}
    pq = [(0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in graph.get(u, {}).items():
            if d + w < dist.get(v, float("inf")):
                dist[v] = d + w
                heapq.heappush(pq, (d + w, v))
    return dict(sorted(dist.items()))


def migration_order(revs: dict[str, str | None]) -> list[str]:
    """C3. Ревизии Alembic: ревизия → down_revision (None — первая). Порядок применения от первой до head.
    Несколько первых, несколько голов, ссылка на несуществующую ревизию или цикл — ValueError."""
    roots = [r for r, d in revs.items() if d is None]
    if any(d is not None and d not in revs for d in revs.values()):
        raise ValueError("ссылка на неизвестную ревизию")
    children: dict[str, list[str]] = {}
    for r, d in revs.items():
        if d is not None:
            children.setdefault(d, []).append(r)
    if len(roots) != 1 or any(len(c) > 1 for c in children.values()):
        raise ValueError("история не линейная (несколько голов или корней)")
    order = [roots[0]]
    while order[-1] in children:
        order.append(children[order[-1]][0])
    if len(order) != len(revs):
        raise ValueError("цикл")
    return order


def diff_lines(a: list[str], b: list[str]) -> list[str]:
    """C4*. Построчный diff по наибольшей общей подпоследовательности: "  x" — общая, "- x" — удалена,
    "+ x" — добавлена. При выборе — сначала удаление, потом добавление."""
    n, m = len(a), len(b)
    L = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            L[i][j] = L[i + 1][j + 1] + 1 if a[i] == b[j] else max(L[i + 1][j], L[i][j + 1])
    out, i, j = [], 0, 0
    while i < n or j < m:
        if i < n and j < m and a[i] == b[j]:
            out.append("  " + a[i])
            i, j = i + 1, j + 1
        elif i < n and (j == m or L[i + 1][j] >= L[i][j + 1]):
            out.append("- " + a[i])
            i += 1
        else:
            out.append("+ " + b[j])
            j += 1
    return out


# ---------- D. Релиз ----------

_SEMVER = re.compile(r"v?(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?")


def semver_key(v: str):
    """D1. Ключ сортировки версий semver: числа; версия с пред-релизом (-rc1) меньше той же без него;
    части пред-релиза через точку: числа меньше строк, числа — как числа. Неверная версия — ValueError."""
    m = _SEMVER.fullmatch(v)
    if not m:
        raise ValueError(v)
    major, minor, patch, pre = m.groups()
    core = (int(major), int(minor), int(patch))
    if pre is None:
        return (*core, 1, ())
    parts = tuple((0, int(p), "") if p.isdigit() else (1, 0, p) for p in pre.split("."))
    return (*core, 0, parts)


def semver_sort(versions: list[str]) -> list[str]:
    """D1. Отсортировать версии по возрастанию."""
    return sorted(versions, key=semver_key)


_CC = re.compile(r"(\w+)(?:\(([\w-]+)\))?(!)?: (.+)")


def next_version(current: str, commits: list[str]) -> str:
    """D2. Conventional commits: "feat: …", "fix(scope): …", "feat!: …" или текст "BREAKING CHANGE" — мажор.
    От current (без пред-релиза): ломающее → x+1.0.0 (при x = 0 — 0.y+1.0), feat → x.y+1.0, fix → x.y.z+1,
    иначе — current. Пред-релиз в current отбрасывается, если есть изменения."""
    m = _SEMVER.fullmatch(current)
    if not m:
        raise ValueError(current)
    x, y, z = map(int, m.groups()[:3])
    level = 0
    for c in commits:
        cm = _CC.match(c)
        if "BREAKING CHANGE" in c or (cm and cm.group(3)):
            level = max(level, 3)
        elif cm and cm.group(1) == "feat":
            level = max(level, 2)
        elif cm and cm.group(1) == "fix":
            level = max(level, 1)
    if level == 0:
        return current
    if level == 3:
        return f"{x + 1}.0.0" if x > 0 else f"0.{y + 1}.0"
    if level == 2:
        return f"{x}.{y + 1}.0"
    return f"{x}.{y}.{z + 1}"


def changelog(version: str, date: str, commits: list[str]) -> str:
    """D2. Раздел CHANGELOG: "## version — date", затем "### Ломающее", "### Новое", "### Исправлено" (только
    непустые), пункты "- описание" (со scope — "- scope: описание") в исходном порядке. Прочие коммиты
    не попадают. Строки через \\n, без пустых строк."""
    groups = {"Ломающее": [], "Новое": [], "Исправлено": []}
    for c in commits:
        cm = _CC.match(c)
        if not cm:
            continue
        typ, scope, bang, text = cm.groups()
        item = f"- {scope}: {text}" if scope else f"- {text}"
        if bang or "BREAKING CHANGE" in c:
            groups["Ломающее"].append(item)
        elif typ == "feat":
            groups["Новое"].append(item)
        elif typ == "fix":
            groups["Исправлено"].append(item)
    out = [f"## {version} — {date}"]
    for g, items in groups.items():
        if items:
            out += [f"### {g}", *items]
    return "\n".join(out)


SECRET_PATTERNS = [
    ("telegram", re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{35}\b")),
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("dsn_password", re.compile(r"\b[a-z+]+://[^\s:/@]+:([^\s@$<{]+)@")),
]


def scan_secrets(text: str) -> list[tuple[int, str]]:
    """D3. Поиск секретов перед публикацией репозитория: (номер строки с 1, вид) по порядку строк, внутри
    строки — в порядке SECRET_PATTERNS. Виды: токен бота Telegram (8–10 цифр, двоеточие, 35 символов
    [A-Za-z0-9_-]), приватный ключ PEM, пароль в DSN (user:пароль@, кроме $VAR, ${VAR} и <…>)."""
    out = []
    for i, ln in enumerate(text.splitlines(), 1):
        for kind, rx in SECRET_PATTERNS:
            if rx.search(ln):
                out.append((i, kind))
    return out
