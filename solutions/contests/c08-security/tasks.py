"""Контест 8 · Безопасность — эталонные решения A–D."""
import hashlib
import hmac
import json
import re
import unicodedata
from collections import defaultdict, deque

# ---------- A. Подписи и пароли ----------

def canonical(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sign(secret: str, payload: dict) -> str:
    """A1. HMAC-SHA256 от канонического JSON (ключи по алфавиту, без пробелов), hex."""
    return hmac.new(secret.encode(), canonical(payload).encode(), hashlib.sha256).hexdigest()


def verify(secret: str, payload: dict, sig: str) -> bool:
    return hmac.compare_digest(sign(secret, payload), sig)


def hash_password(password: str, salt: bytes, iterations: int = 100_000) -> str:
    """A2. "pbkdf2_sha256$<итерации>$<соль hex>$<хеш hex>"."""
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    return f"pbkdf2_sha256${iterations}${salt.hex()}${dk.hex()}"


def check_password(password: str, stored: str) -> bool:
    try:
        algo, it, salt, _ = stored.split("$")
        if algo != "pbkdf2_sha256":
            return False
        expected = hash_password(password, bytes.fromhex(salt), int(it))
    except ValueError:
        return False
    return hmac.compare_digest(expected, stored)


def naive_equal_steps(a: str, b: str) -> tuple[bool, int]:
    """A3. Наивное сравнение: длины разные — (False, 0); иначе сравниваем символы слева направо
    до первого несовпадения. steps — сколько пар символов сравнили."""
    if len(a) != len(b):
        return False, 0
    steps = 0
    for x, y in zip(a, b):
        steps += 1
        if x != y:
            return False, steps
    return True, steps


def timing_attack(oracle, alphabet: str, length: int) -> str:
    """A4*. oracle(guess) -> (равно ли, steps) как в A3 для секрета длины length. Восстановить секрет,
    вызвав oracle не больше len(alphabet) * length раз."""
    known = ""
    for pos in range(length):
        pad = alphabet[0] * (length - pos - 1)
        best, best_steps = alphabet[0], -1
        for c in alphabet:
            ok, steps = oracle(known + c + pad)
            if ok:
                return known + c + pad
            if steps > best_steps:
                best, best_steps = c, steps
        known += best
    return known


# ---------- B. Ввод от игроков ----------

RESERVED = {"admin", "system", "bot"}


def safe_name(name: str) -> str:
    """B1. Имя игрока: NFC, обрезать пробелы по краям, несколько пробелов подряд — один.
    Длина 2..16, символы — буквы и цифры любого алфавита, "_", "-", пробел. Не admin/system/bot
    (без учёта регистра). Иначе ValueError."""
    s = re.sub(r" +", " ", unicodedata.normalize("NFC", name).strip())
    if not 2 <= len(s) <= 16:
        raise ValueError("длина")
    if not all(ch.isalnum() or ch in "_- " for ch in s):
        raise ValueError("символы")
    if s.lower() in RESERVED:
        raise ValueError("занято")
    return s


ESCAPES = {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#x27;"}


def escape_html(text: str) -> str:
    return "".join(ESCAPES.get(ch, ch) for ch in text)


def render_rating(rows: list[tuple[str, int]]) -> str:
    """B2. HTML рейтинга: по убыванию очков, при равенстве — по имени."""
    items = [f"<li><b>{escape_html(n)}</b> — {s}</li>" for n, s in sorted(rows, key=lambda r: (-r[1], r[0]))]
    return "\n".join(["<ol>", *items, "</ol>"])


SQL_RISK = re.compile(r"""\b(?:execute|text)\(\s*(?:f["']|(["'])[^"']*\1\s*(?:%|\+|\.format\())""")


def find_sql_injection(code: str) -> list[int]:
    """B3. Номера строк (с 1), где в execute( или text( первым аргументом идёт f-строка
    или строковый литерал, к которому применяют %, + или .format(."""
    return [i for i, line in enumerate(code.splitlines(), 1) if SQL_RISK.search(line)]


# ---------- C. Лимиты ----------

def fixed_window(times: list[int], limit: int, window: int) -> list[bool]:
    """C1. Фиксированные окна [k·window, (k+1)·window): в каждом не больше limit разрешённых."""
    used: dict[int, int] = defaultdict(int)
    out = []
    for t in times:
        k = t // window
        ok = used[k] < limit
        used[k] += ok
        out.append(ok)
    return out


def gcra(times: list[int], period: int, burst: int) -> list[bool]:
    """C2. GCRA: TAT (теоретическое время прихода) сначала 0. На запрос в t: tat = max(TAT, t);
    если tat − t > period·(burst − 1) — отказ (TAT не меняем), иначе разрешить и TAT = tat + period."""
    tat, out = 0, []
    for t in times:
        cur = max(tat, t)
        if cur - t > period * (burst - 1):
            out.append(False)
        else:
            tat = cur + period
            out.append(True)
    return out


def fail2ban(failures: list[tuple[int, str]], threshold: int, window: int, ban: int) -> list[tuple[str, int, int]]:
    """C3. Неудачные входы (ts, ip) по времени. Если у ip набралось threshold неудач в (t − window, t] —
    бан [t, t + ban). Неудачи во время бана не считаются; после бана счёт с нуля."""
    recent: dict[str, deque[int]] = defaultdict(deque)
    banned_until: dict[str, int] = {}
    bans = []
    for ts, ip in sorted(failures, key=lambda f: f[0]):
        if ts < banned_until.get(ip, -1):
            continue
        q = recent[ip]
        q.append(ts)
        while q[0] <= ts - window:
            q.popleft()
        if len(q) >= threshold:
            bans.append((ip, ts, ts + ban))
            banned_until[ip] = ts + ban
            q.clear()
    return bans


def clusters(logins: list[tuple[str, str, str]]) -> list[list[str]]:
    """C4*. Входы (user, ip, device). Пользователи связаны, если у них общий ip или устройство
    (и цепочкой через других). Группы от двух человек, внутри по имени, группы по первому имени."""
    parent: dict[str, str] = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        parent[find(a)] = find(b)

    for user, ip, device in logins:
        union("u:" + user, "i:" + ip)
        union("u:" + user, "d:" + device)
    groups: dict[str, set[str]] = defaultdict(set)
    for node in list(parent):
        if node.startswith("u:"):
            groups[find(node)].add(node[2:])
    return sorted(sorted(g) for g in groups.values() if len(g) >= 2)


# ---------- D. Античит ----------

POINTS = {"eat": 10, "gold": 50}


def replay_score(events: list[str], claimed: int) -> tuple[int, bool]:
    """D1. Пересчитать счёт змейки по событиям сервера: eat +10, gold +50, умноженные на серию.
    Серия растёт на 1 (не больше 3), если с прошлой еды прошло не больше 2 tick, иначе сбрасывается в 1.
    После die события не считаем. Неизвестное событие — ValueError."""
    score, mult, ticks, eaten = 0, 1, 0, False
    for e in events:
        if e == "die":
            break
        if e == "tick":
            ticks += 1
        elif e in POINTS:
            mult = min(mult + 1, 3) if eaten and ticks <= 2 else 1
            score += POINTS[e] * mult
            eaten, ticks = True, 0
        else:
            raise ValueError(e)
    return score, score == claimed


def seq_check(messages: list[tuple[str, int]]) -> list[str]:
    """D2. Сообщения (игрок, seq). Для каждого: "dup" — seq не больше последнего принятого (не принимаем);
    "gap" — пропуск (seq больше ожидаемого; принимаем); "ok". Ожидаемый первый seq — 1."""
    last: dict[str, int] = {}
    out = []
    for player, seq in messages:
        prev = last.get(player, 0)
        if seq <= prev:
            out.append("dup")
            continue
        out.append("ok" if seq == prev + 1 else "gap")
        last[player] = seq
    return out


def fog_of_war(units: list[tuple[str, int, int]], player: str, radius: int) -> list[tuple[str, int, int]]:
    """D3. Что отправить игроку: свои юниты и чужие на расстоянии Чебышёва ≤ radius от любого своего.
    Порядок — как во входе."""
    mine = [(x, y) for o, x, y in units if o == player]
    return [u for u in units
            if u[0] == player or any(max(abs(u[1] - x), abs(u[2] - y)) <= radius for x, y in mine)]
