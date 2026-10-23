"""Сканер секретов: правила, энтропия, маскирование, обход дерева, сканирование diff."""
import fnmatch
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

# ---------- 1. Энтропия ----------


def shannon_entropy(s: str) -> float:
    """Бит на символ: −Σ p·log2(p). Пустая строка → 0.0."""
    if not s:
        return 0.0
    n = len(s)
    return -sum(c / n * math.log2(c / n) for c in Counter(s).values())


def looks_random(s: str, min_len: int = 16, threshold: float = 3.5) -> bool:
    return len(s) >= min_len and shannon_entropy(s) >= threshold


# ---------- 2–3. Правила и маскирование ----------

RULES: dict[str, re.Pattern] = {
    "telegram_bot_token": re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{35}\b"),
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36}\b"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    "url_password": re.compile(r"\b[a-z][a-z0-9+.-]*://[^/\s:@]+:([^/\s@]+)@"),
}
ASSIGN = re.compile(
    r"""(?i)\b[\w.-]*?(password|passwd|pwd|secret|token|api_?key)[\w-]*\s*[:=]\s*(['"]?)([^'"\s#]+)""")
PLACEHOLDERS = {"changeme", "change_me", "example", "none", "null", "true", "false", "secret", "password"}


def is_placeholder(value: str, quoted: bool) -> bool:
    v = value.lower()
    if v in PLACEHOLDERS or set(v) <= {"x", "*", "."} or v.startswith(("your_", "your-", "<", "${", "$", "{{")):
        return True
    return not quoted and any(c in value for c in "()[]")  # выражение в коде: os.getenv("X"), cfg["x"]
IGNORE_MARK = "secret-scan: ignore"


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    rule: str
    preview: str


def mask(secret: str) -> str:
    """Первые 4 и последние 2 символа, между ними «…». Короче 10 символов → только «***»."""
    if len(secret) < 10:
        return "***"
    return f"{secret[:4]}…{secret[-2:]}"


def scan_line(text: str) -> list[tuple[str, str]]:
    """(правило, найденное значение) по порядку RULES; generic_assignment — последним."""
    if IGNORE_MARK in text:
        return []
    found = []
    for rule, rx in RULES.items():
        for m in rx.finditer(text):
            found.append((rule, m.group(1) if rx.groups else m.group(0)))
    if not found:
        for m in ASSIGN.finditer(text):
            kind, quote, value = m.groups()
            if is_placeholder(value, bool(quote)):
                continue
            if kind.lower() in ("password", "passwd", "pwd"):
                ok = len(value) >= 6                      # пароль ловим любой, даже простой
            else:
                ok = looks_random(value, min_len=8, threshold=3.0)
            if ok:
                found.append(("generic_assignment", value))
    return found


def scan_text(text: str, path: str = "<text>") -> list[Finding]:
    out = []
    for no, line in enumerate(text.splitlines(), 1):
        for rule, value in scan_line(line):
            out.append(Finding(path, no, rule, mask(value)))
    return out


# ---------- 4. Обход дерева ----------

SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__"}


def _ignored(rel: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(rel, p) or fnmatch.fnmatch(Path(rel).name, p) for p in patterns)


def scan_tree(root: str | Path) -> list[Finding]:
    root = Path(root)
    ign = root / ".secretsignore"
    patterns = []
    if ign.exists():
        patterns = [ln.strip() for ln in ign.read_text(encoding="utf-8").splitlines()
                    if ln.strip() and not ln.lstrip().startswith("#")]
    out = []
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root).as_posix()
        if not p.is_file() or any(part in SKIP_DIRS for part in p.relative_to(root).parts):
            continue
        if _ignored(rel, patterns):
            continue
        data = p.read_bytes()
        if b"\0" in data[:1024]:
            continue
        out += scan_text(data.decode("utf-8", errors="replace"), rel)
    return out


# ---------- 5. .env ----------

ENV_LINE = re.compile(r"^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$")


def parse_env(text: str) -> dict[str, str]:
    env = {}
    for no, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = ENV_LINE.match(line)
        if not m:
            raise ValueError(f"строка {no}: {raw!r}")
        key, value = m.groups()
        if value[:1] in ("'", '"'):
            q = value[0]
            end = value.find(q, 1)
            if end == -1:
                raise ValueError(f"строка {no}: нет закрывающей кавычки")
            value = value[1:end]
        else:
            value = re.split(r"\s+#", value, maxsplit=1)[0].strip()
        env[key] = value
    return env


def check_env(example: str, actual: str) -> dict[str, list[str]]:
    """Сравнить .env.example и .env: каких ключей не хватает, какие лишние, какие пустые."""
    ex, ac = parse_env(example), parse_env(actual)
    return {
        "missing": sorted(set(ex) - set(ac)),
        "extra": sorted(set(ac) - set(ex)),
        "empty": sorted(k for k in ex if k in ac and ac[k] == ""),
    }


# ---------- 6. diff ----------

HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def scan_diff(diff: str) -> list[Finding]:
    """Только добавленные строки; номер строки — в новой версии файла."""
    out = []
    path, line_no = None, 0
    for raw in diff.splitlines():
        if raw.startswith("+++ "):
            target = raw[4:].strip()
            path = None if target == "/dev/null" else target.removeprefix("b/")
            continue
        if raw.startswith("--- "):
            continue
        m = HUNK.match(raw)
        if m:
            line_no = int(m.group(1))
            continue
        if path is None:
            continue
        if raw.startswith("+"):
            for rule, value in scan_line(raw[1:]):
                out.append(Finding(path, line_no, rule, mask(value)))
            line_no += 1
        elif raw.startswith(" "):
            line_no += 1
    return out


# ---------- 7*. Очистка логов ----------


def redact(text: str, secrets: list[str]) -> str:
    """Заменить каждое вхождение секрета на «***», в том числе в URL-кодировке и base64."""
    import base64
    from urllib.parse import quote

    variants = set()
    for s in secrets:
        if not s:
            continue
        variants |= {s, quote(s, safe=""), base64.b64encode(s.encode()).decode().rstrip("=")}
    for v in sorted(variants, key=len, reverse=True):
        text = text.replace(v, "***")
    return text
