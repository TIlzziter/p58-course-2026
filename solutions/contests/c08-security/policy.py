"""E5*. Правила доступа агента с шаблонами и фигурными скобками."""
import re
from fnmatch import fnmatchcase


def expand(pattern: str) -> list[str]:
    """"shell:git {status,diff}*" -> ["shell:git status*", "shell:git diff*"]. Скобки не вложены, их может быть несколько."""
    m = re.search(r"\{([^{}]*)\}", pattern)
    if not m:
        return [pattern]
    return [x for alt in m.group(1).split(",") for x in expand(pattern[:m.start()] + alt + pattern[m.end():])]


def audit_policy(rules: list[tuple[str, str]], calls: list[str]) -> tuple[list[bool], list[int]]:
    """Правила (allow|deny, шаблон) по порядку, первое совпавшее решает; не совпало ни одно — deny.
    Шаблон — fnmatchcase с раскрытием {a,b}. Ответ: решения по вызовам и номера правил (с 0),
    которые ни разу не решили."""
    expanded = [expand(p) for _, p in rules]
    used = set()
    out = []
    for call in calls:
        for i, ((action, _), pats) in enumerate(zip(rules, expanded)):
            if any(fnmatchcase(call, p) for p in pats):
                used.add(i)
                out.append(action == "allow")
                break
        else:
            out.append(False)
    return out, [i for i in range(len(rules)) if i not in used]
