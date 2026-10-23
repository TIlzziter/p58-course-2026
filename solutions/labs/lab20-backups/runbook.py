"""Задача 6. Проверка runbook восстановления."""
import re

REQUIRED = ["Когда применять", "Перед началом", "Шаги", "Проверка", "Откат", "Контакты"]
SECRET = re.compile(r"(?i)\b(password|passwd|secret|token|pgpassword)\b\s*[=:]\s*(\S+)")


def check_runbook(text: str) -> list[str]:
    """Список проблем (пустой — runbook годится), в таком порядке:
    1) "нет раздела: X" — для каждого раздела REQUIRED без заголовка `## X` (в порядке REQUIRED);
    2) "мало шагов: N" — в разделе «Шаги» меньше 3 пунктов нумерованного списка (`1. …`);
    3) "шаг K без команды" — для каждого пункта «Шагов» без `кода в обратных кавычках`;
    4) "секрет в строке L" — номер строки (с 1), где пароль/секрет/токен записан значением, а не
       переменной: `PGPASSWORD=$PGPASSWORD`, `${DB_PASSWORD}` и `<пароль>` допустимы."""
    lines = text.splitlines()
    heads = {m.group(1).strip() for m in (re.match(r"^##\s+(.+)$", ln) for ln in lines) if m}
    problems = [f"нет раздела: {r}" for r in REQUIRED if r not in heads]
    steps, inside = [], False
    for ln in lines:
        if ln.startswith("## "):
            inside = ln[3:].strip() == "Шаги"
            continue
        if inside and re.match(r"^\s*\d+\.\s", ln):
            steps.append(ln)
    if "Шаги" in heads and len(steps) < 3:
        problems.append(f"мало шагов: {len(steps)}")
    for k, s in enumerate(steps, 1):
        if not re.search(r"`[^`]+`", s):
            problems.append(f"шаг {k} без команды")
    for i, ln in enumerate(lines, 1):
        for m in SECRET.finditer(ln):
            v = m.group(2).strip("`'\"")
            if not (v.startswith("$") or v.startswith("<")):
                problems.append(f"секрет в строке {i}")
                break
    return problems
