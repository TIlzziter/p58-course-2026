"""Проверки командного Git-процесса «Проекта 58». Эталонное решение."""
import re

BRANCH_TYPES = ("feature", "fix", "docs", "chore")
COMMIT_AREAS = ("bot", "api", "game", "web", "tests", "docs", "infra", "ci")
PR_SECTIONS = ("## Что сделано", "## Как проверить", "## Что сгенерировал агент")
AGENTS_SECTIONS = ("## Стек", "## Правила", "## Как проверить")

TRANSLIT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e", "ж": "zh",
    "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o",
    "п": "p", "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f", "х": "h",
    "ц": "c", "ч": "ch", "ш": "sh", "щ": "sch", "ъ": "", "ы": "y", "ь": "",
    "э": "e", "ю": "yu", "я": "ya",
}
BRANCH_RE = re.compile(r"^(feature|fix|docs|chore)/[1-9]\d*-[a-z0-9]+(-[a-z0-9]+)*$")
LOG_RE = re.compile(r"^([0-9a-f]{7,40}) (.*)$")
SECRET_RES = (
    re.compile(r"(token|secret|password|passwd|api_key|apikey)\w*\s*=\s*\S+", re.IGNORECASE),
    re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{30,}\b"),          # токен Telegram-бота
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
)


def slugify(title: str) -> str:
    parts = []
    for ch in title.lower():
        if ch in TRANSLIT:
            parts.append(TRANSLIT[ch])
        elif ch.isascii() and ch.isalnum():
            parts.append(ch)
        else:
            parts.append("-")
    return re.sub(r"-+", "-", "".join(parts)).strip("-")


def branch_name(issue: int, title: str, kind: str = "feature") -> str:
    if kind not in BRANCH_TYPES:
        raise ValueError(f"неизвестный тип ветки: {kind}")
    if issue < 1:
        raise ValueError("номер issue должен быть положительным")
    slug = slugify(title)
    if not slug:
        raise ValueError("пустой заголовок")
    return f"{kind}/{issue}-{slug}"


def is_valid_branch(name: str) -> bool:
    return BRANCH_RE.fullmatch(name) is not None


def commit_problems(message: str) -> list[str]:
    lines = message.splitlines()
    first = lines[0].strip() if lines else ""
    if not first:
        return ["пустое сообщение"]
    problems = []
    area, sep, text = first.partition(": ")
    if not sep:
        problems.append("нет области: нужен формат «область: что сделано»")
    else:
        if area not in COMMIT_AREAS:
            problems.append(f"неизвестная область {area!r}")
        if not text.strip():
            problems.append("пустое описание")
        elif text[0].isupper():
            problems.append("описание с большой буквы")
    if len(first) > 72:
        problems.append("первая строка длиннее 72 символов")
    if first.endswith("."):
        problems.append("точка в конце")
    return problems


def parse_log(log: str) -> list[dict]:
    result = []
    for line in log.splitlines():
        line = line.strip()
        m = LOG_RE.match(line)
        if not m:
            continue
        sha, msg = m.groups()
        area, sep, text = msg.partition(": ")
        if sep and area in COMMIT_AREAS:
            result.append({"hash": sha, "area": area, "text": text})
        else:
            result.append({"hash": sha, "area": None, "text": msg})
    return result


def count_by_area(log: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for commit in parse_log(log):
        if commit["area"] is not None:
            counts[commit["area"]] = counts.get(commit["area"], 0) + 1
    return counts


def pr_problems(description: str) -> list[str]:
    problems = [f"нет раздела {s!r}" for s in PR_SECTIONS if s not in description]
    if not re.search(r"\b(Closes|Fixes) #\d+\b", description):
        problems.append("нет ссылки на issue (Closes #N)")
    return problems


def agents_md_problems(text: str) -> list[str]:
    headers = {line.strip() for line in text.splitlines()}
    problems = [f"нет раздела {s!r}" for s in AGENTS_SECTIONS if s not in headers]
    for number, line in enumerate(text.splitlines(), 1):
        if any(r.search(line) for r in SECRET_RES):
            problems.append(f"строка {number}: похоже на секрет")
    return problems
