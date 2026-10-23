"""Контест 1 — эталонные решения задач A–C."""
import re
from collections import Counter
from itertools import combinations

BRANCH_RE = re.compile(r"^(feature|fix|docs|chore)/(\d+)-[a-z0-9]+(-[a-z0-9]+)*$")
ROLES = {"аналитика", "бэкенд", "фронтенд", "тестирование", "devops", "дизайн"}
STORY_RE = re.compile(r"^Как (.+?), я хочу (.+?), чтобы (.+?)\.?$")


# A1
def issue_number(branch: str) -> int | None:
    m = BRANCH_RE.match(branch)
    return int(m.group(2)) if m else None


# A2
def game_commits(messages: list[str]) -> list[str]:
    result = []
    for msg in messages:
        if msg == "--":
            break
        if msg.startswith("Merge"):
            continue
        if msg.startswith("game: "):
            result.append(msg)
    return result


# A3
def can_merge(verdicts: list[str]) -> bool:
    if "approve" not in verdicts:
        return False
    if "changes" not in verdicts:
        return True
    last_changes = len(verdicts) - 1 - verdicts[::-1].index("changes")
    return "approve" in verdicts[last_changes + 1:]


# B1
def top_authors(authors: list[str]) -> list[tuple[str, int]]:
    return sorted(Counter(authors).items(), key=lambda p: (-p[1], p[0]))


# B2
def free_roles(students: dict[str, tuple[str, str]]) -> set[str]:
    return ROLES - {main for main, _ in students.values()}


# B3
def conflict_files(a: list[str], b: list[str]) -> list[str]:
    return sorted(set(a) & set(b))


# B4*
def split_teams(exp: list[int]) -> int:
    total = sum(exp)
    best = total
    for team in combinations(range(len(exp)), len(exp) // 2):
        s = sum(exp[i] for i in team)
        best = min(best, abs(total - 2 * s))
    return best


# C1
def done_percent(text: str) -> int | None:
    boxes = re.findall(r"^\s*- \[([ xX])\]", text, re.M)
    if not boxes:
        return None
    done = sum(1 for b in boxes if b in "xX")
    return round(done * 100 / len(boxes))


# C2
def parse_story(text: str) -> dict | None:
    m = STORY_RE.match(text.strip())
    if not m:
        return None
    return {"role": m.group(1), "want": m.group(2), "why": m.group(3)}


# C3
def validate_move(msg) -> list[str]:
    if not isinstance(msg, dict):
        return ["сообщение должно быть объектом"]
    errors = []
    if msg.get("type") != "move":
        errors.append("type должен быть move")
    col = msg.get("col")
    if not isinstance(col, int) or isinstance(col, bool):
        errors.append("col должен быть целым числом")
    elif not 0 <= col <= 6:
        errors.append("col вне диапазона 0..6")
    extra = sorted(set(msg) - {"type", "col"})
    if extra:
        errors.append("лишние ключи: " + ", ".join(extra))
    return errors
