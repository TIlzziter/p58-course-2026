"""Контест 5 · Конвейеры и секреты — эталонные решения A1–D3."""
import re

# ---------- A. Конвейер ----------


def stages(jobs: dict[str, list[str]]) -> list[list[str]] | None:
    """A1. Волны параллельного запуска: в волне — все jobs, чьи needs уже выполнены. Цикл → None."""
    done: set[str] = set()
    waves = []
    while len(done) < len(jobs):
        wave = sorted(j for j, needs in jobs.items() if j not in done and all(n in done for n in needs))
        if not wave:
            return None
        waves.append(wave)
        done |= set(wave)
    return waves


def pipeline_time(jobs: dict[str, list[str]], duration: dict[str, int]) -> int:
    """A2. Время всего конвейера при неограниченном числе машин — длина критического пути."""
    finish: dict[str, int] = {}

    def end(j: str) -> int:
        if j not in finish:
            finish[j] = max((end(n) for n in jobs[j]), default=0) + duration[j]
        return finish[j]

    return max((end(j) for j in jobs), default=0)


def affected(jobs: dict[str, list[str]], failed: str) -> list[str]:
    """A3. Какие jobs будут пропущены, если упал failed (все, кто прямо или косвенно от него зависит)."""
    out: set[str] = set()
    changed = True
    while changed:
        changed = False
        for j, needs in jobs.items():
            if j not in out and j != failed and any(n == failed or n in out for n in needs):
                out.add(j)
                changed = True
    return sorted(out)


def runners_time(jobs: dict[str, list[str]], duration: dict[str, int], k: int) -> int:
    """A4*. k машин. Как только машина свободна, она берёт готовый job с наименьшим именем."""
    t = 0
    done: set[str] = set()
    running: dict[str, int] = {}  # job → время окончания
    while len(done) < len(jobs):
        ready = sorted(j for j, needs in jobs.items()
                       if j not in done and j not in running and all(n in done for n in needs))
        while ready and len(running) < k:
            j = ready.pop(0)
            running[j] = t + duration[j]
        t = min(running.values())
        for j in [j for j, e in running.items() if e == t]:
            del running[j]
            done.add(j)
    return t


# ---------- B. Версии ----------


def _ver(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in v.split("."))


def sort_versions(vs: list[str]) -> list[str]:
    """B1. По возрастанию как версии; при равенстве чисел короче — раньше (3.12 < 3.12.0)."""
    return sorted(vs, key=lambda v: (_ver(v), len(v.split("."))))


def _cmp(a: tuple[int, ...], b: tuple[int, ...]) -> int:
    n = max(len(a), len(b))
    a, b = a + (0,) * (n - len(a)), b + (0,) * (n - len(b))
    return (a > b) - (a < b)


def satisfies(version: str, spec: str) -> bool:
    """B2. Условия через запятую: >=, <=, >, <, ==, !=; в == и != можно `*` в конце (3.12.*)."""
    v = _ver(version)
    for cond in (c.strip() for c in spec.split(",") if c.strip()):
        m = re.fullmatch(r"(>=|<=|==|!=|>|<)\s*([\d.]+(?:\.\*)?)", cond)
        if not m:
            raise ValueError(cond)
        op, target = m.groups()
        if target.endswith(".*"):
            prefix = _ver(target[:-2])
            hit = v[:len(prefix)] == prefix
            ok = hit if op == "==" else (not hit if op == "!=" else None)
            if ok is None:
                raise ValueError(cond)
        else:
            c = _cmp(v, _ver(target))
            ok = {">=": c >= 0, "<=": c <= 0, ">": c > 0, "<": c < 0, "==": c == 0, "!=": c != 0}[op]
        if not ok:
            return False
    return True


def bump(version: str, part: str) -> str:
    """B3. Семантическое версионирование: major.minor.patch; младшие части обнуляются."""
    major, minor, patch = _ver(version)
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    if part == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise ValueError(part)


# ---------- C. Секреты и окружение ----------


def env_diff(old: dict[str, str], new: dict[str, str]) -> list[str]:
    """C1. Изменения окружения без значений: «+ KEY», «- KEY», «~ KEY», по ключу."""
    out = []
    for k in sorted(set(old) | set(new)):
        if k not in old:
            out.append(f"+ {k}")
        elif k not in new:
            out.append(f"- {k}")
        elif old[k] != new[k]:
            out.append(f"~ {k}")
    return out


INTERP = re.compile(r"\$\$|\$\{([A-Za-z_]\w*)(?:(:?-)([^}]*))?\}|\$([A-Za-z_]\w*)")


def interpolate(value: str, env: dict[str, str]) -> str:
    """C2. Подстановка как в docker compose: $VAR, ${VAR}, ${VAR:-def} (нет или пусто), ${VAR-def} (нет), $$ → $."""
    def sub(m: re.Match) -> str:
        if m.group(0) == "$$":
            return "$"
        name = m.group(1) or m.group(4)
        op, default = m.group(2), m.group(3)
        if op == ":-":
            return env.get(name) or default
        if op == "-":
            return env[name] if name in env else default
        return env.get(name, "")
    return INTERP.sub(sub, value)


URL = re.compile(r"^([a-z][a-z0-9+.-]*://)([^/@:]*)(?::([^/@]*))?@")


def redact_url(url: str) -> str:
    """C3. Пароль в URL → ***; пользователь остаётся. Нет пароля — без изменений."""
    m = URL.match(url)
    if not m or m.group(3) is None:
        return url
    return f"{m.group(1)}{m.group(2)}:***@{url[m.end():]}"


TOKEN = re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{35}\b")


def leaked_tokens(commits: list[dict]) -> list[tuple[str, str, bool]]:
    """C4*. История: коммиты по порядку, у каждого sha и files: {путь: (добавленные строки, удалённые строки)}.

    Вернуть (маска токена, sha первого появления, есть ли он в HEAD) по порядку появления.
    Маска — первые 4 и последние 2 символа через «…».
    """
    first: dict[str, str] = {}
    alive: dict[tuple[str, str], int] = {}  # (токен, путь) → сколько строк с ним сейчас в файле
    for c in commits:
        for path, (added, removed) in c["files"].items():
            for line in removed:
                for t in TOKEN.findall(line):
                    alive[(t, path)] = alive.get((t, path), 0) - 1
            for line in added:
                for t in TOKEN.findall(line):
                    first.setdefault(t, c["sha"])
                    alive[(t, path)] = alive.get((t, path), 0) + 1
    out = []
    for t, sha in first.items():
        present = any(cnt > 0 for (tok, _), cnt in alive.items() if tok == t)
        out.append((f"{t[:4]}…{t[-2:]}", sha, present))
    return out


# ---------- D. Деплой ----------

TAG = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")


def next_release(tags: list[str], part: str = "patch") -> str:
    """D1. Следующий тег после наибольшего корректного vX.Y.Z; корректных нет → v0.1.0."""
    valid = [tuple(map(int, m.groups())) for t in tags if (m := TAG.match(t))]
    if not valid:
        return "v0.1.0"
    return "v" + bump(".".join(map(str, max(valid))), part)


def rollback_target(deploys: list[tuple[str, str]]) -> str | None:
    """D2. deploys — (версия, ok|failed) по времени. Текущая — последняя ok. Откат — на предыдущую ok,
    отличную от текущей. Нет такой → None."""
    oks = [v for v, s in deploys if s == "ok"]
    if not oks:
        return None
    current = oks[-1]
    for v in reversed(oks[:-1]):
        if v != current:
            return v
    return None


def canary(errors: list[int], requests: list[int], threshold: float, window: int) -> int | None:
    """D3. Минута (с нуля), в которую доля ошибок за последние window минут (включая эту) впервые
    строго больше threshold. Окно неполное в начале — считаем по тому, что есть. Запросов 0 → доля 0."""
    for i in range(len(errors)):
        lo = max(0, i - window + 1)
        req = sum(requests[lo:i + 1])
        rate = sum(errors[lo:i + 1]) / req if req else 0.0
        if rate > threshold:
            return i
    return None


__all__ = ["stages", "pipeline_time", "affected", "runners_time", "sort_versions", "satisfies", "bump",
           "env_diff", "interpolate", "redact_url", "leaked_tokens", "next_release", "rollback_target", "canary"]
