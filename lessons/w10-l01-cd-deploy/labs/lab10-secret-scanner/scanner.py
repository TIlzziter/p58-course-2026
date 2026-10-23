"""Сканер секретов: правила, энтропия, маскирование, обход дерева, сканирование diff.

Черновик от «агента»: работает на паре примеров из головы, тесты — нет. Задачи 1–7 описаны в README.
"""
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

# ---------- 1. Энтропия ----------


def shannon_entropy(s: str) -> float:
    """Бит на символ: −Σ p·log2(p). Пустая строка → 0.0."""
    n = len(s)
    return -sum(c / n * math.log(c / n) for c in Counter(s).values())


def looks_random(s: str, min_len: int = 16, threshold: float = 3.5) -> bool:
    return shannon_entropy(s) >= threshold


# ---------- 2–3. Правила и маскирование ----------

RULES: dict[str, re.Pattern] = {
    "telegram_bot_token": re.compile(r"\d+:[A-Za-z0-9]+"),
    "github_token": re.compile(r"ghp_[A-Za-z0-9]{36}"),
    "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    # TODO: private_key, url_password (пароль внутри postgresql://user:pass@host)
}
ASSIGN = re.compile(r"""(?i)(password|secret|token|api_?key)\s*[:=]\s*['"]?([^'"\s#]+)""")
IGNORE_MARK = "secret-scan: ignore"


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    rule: str
    preview: str


def mask(secret: str) -> str:
    """Первые 4 и последние 2 символа, между ними «…». Короче 10 символов → только «***»."""
    return secret[:4] + "…"


def scan_line(text: str) -> list[tuple[str, str]]:
    """(правило, найденное значение) по порядку RULES; generic_assignment — только если остальные молчат."""
    found = []
    for rule, rx in RULES.items():
        for m in rx.finditer(text):
            found.append((rule, m.group(0)))
    for m in ASSIGN.finditer(text):
        if len(m.group(2)) >= 8:
            found.append(("generic_assignment", m.group(2)))
    return found


def scan_text(text: str, path: str = "<text>") -> list[Finding]:
    out = []
    for no, line in enumerate(text.splitlines()):
        for rule, value in scan_line(line):
            out.append(Finding(path, no, rule, mask(value)))
    return out


# ---------- 4. Обход дерева ----------

SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__"}


def scan_tree(root: str | Path) -> list[Finding]:
    """Все текстовые файлы под root (кроме SKIP_DIRS, двоичных и шаблонов из .secretsignore), по порядку путей."""
    raise NotImplementedError


# ---------- 5. .env ----------


def parse_env(text: str) -> dict[str, str]:
    env = {}
    for line in text.splitlines():
        if line and not line.startswith("#"):
            key, value = line.split("=")
            env[key] = value
    return env


def check_env(example: str, actual: str) -> dict[str, list[str]]:
    """Сравнить .env.example и .env: каких ключей не хватает (missing), какие лишние (extra), какие пустые (empty)."""
    raise NotImplementedError


# ---------- 6. diff ----------


def scan_diff(diff: str) -> list[Finding]:
    """Только добавленные строки; номер строки — в новой версии файла."""
    raise NotImplementedError


# ---------- 7*. Очистка логов ----------


def redact(text: str, secrets: list[str]) -> str:
    """Заменить каждое вхождение секрета на «***», в том числе в URL-кодировке и base64."""
    for s in secrets:
        text = text.replace(s, "***")
    return text
