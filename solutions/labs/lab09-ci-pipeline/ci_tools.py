"""Инструменты для GitHub Actions: загрузка, порядок jobs, матрица, линтер, подстановка выражений."""
import itertools
import re

import yaml

# ---------- 1. Загрузка ----------


def _norm_events(on) -> dict:
    if isinstance(on, str):
        return {on: {}}
    if isinstance(on, list):
        return {e: {} for e in on}
    if isinstance(on, dict):
        return {e: (v or {}) for e, v in on.items()}
    raise ValueError("непонятный on")


def load_workflow(text: str) -> dict:
    """YAML 1.1 читает ключ `on` как True — возвращаем ему имя и приводим к словарю «событие → настройки»."""
    wf = yaml.safe_load(text)
    if not isinstance(wf, dict) or "jobs" not in wf:
        raise ValueError("нет jobs")
    if True in wf:
        wf["on"] = wf.pop(True)
    if "on" not in wf:
        raise ValueError("нет on")
    wf["on"] = _norm_events(wf["on"])
    return wf


# ---------- 2. Порядок jobs ----------


def _needs(job: dict) -> list[str]:
    n = job.get("needs", [])
    return [n] if isinstance(n, str) else list(n)


def job_order(wf: dict) -> list[str]:
    jobs = wf["jobs"]
    names = list(jobs)
    deps = {name: _needs(job) for name, job in jobs.items()}
    for name, ds in deps.items():
        for d in ds:
            if d not in jobs:
                raise ValueError(f"{name}: неизвестный job {d}")
    done: list[str] = []
    while len(done) < len(names):
        ready = [n for n in names if n not in done and all(d in done for d in deps[n])]
        if not ready:
            raise ValueError("цикл в needs")
        done.append(ready[0])
    return done


# ---------- 3. Матрица ----------


def expand_matrix(job: dict) -> list[dict]:
    matrix = (job.get("strategy") or {}).get("matrix")
    if not matrix:
        return [{}]
    base_keys = [k for k in matrix if k not in ("include", "exclude")]
    combos = [dict(zip(base_keys, values)) for values in itertools.product(*(matrix[k] for k in base_keys))]
    if not base_keys:  # матрица только из include — каждая запись отдельный запуск
        return [dict(inc) for inc in matrix.get("include", [])] or [{}]
    for ex in matrix.get("exclude", []):
        combos = [c for c in combos if not all(c.get(k) == v for k, v in ex.items())]
    for inc in matrix.get("include", []):
        matched = False
        for c in combos:
            if all(c.get(k) == v for k, v in inc.items() if k in base_keys):
                c.update({k: v for k, v in inc.items() if k not in base_keys})
                matched = True
        if not matched:
            combos.append(dict(inc))
    return combos


# ---------- 4. Линтер ----------

MOVING_REFS = {"main", "master", "latest", "head"}


def _steps(job: dict) -> list[dict]:
    return job.get("steps") or []


def lint_workflow(wf: dict) -> list[str]:
    issues: list[str] = []
    top_perm = "permissions" in wf
    pr_target = "pull_request_target" in wf["on"]
    for name, job in wf["jobs"].items():
        if not top_perm and "permissions" not in job:
            issues.append(f"no_permissions:{name}")
        if "timeout-minutes" not in job:
            issues.append(f"no_timeout:{name}")
        matrix = (job.get("strategy") or {}).get("matrix") or {}
        for key, values in matrix.items():
            if key not in ("include", "exclude") and isinstance(values, list) and \
                    any(isinstance(v, float) for v in values):
                issues.append(f"float_version:{name}")
        for step in _steps(job):
            uses = step.get("uses")
            if uses and not uses.startswith(("./", "docker://")):
                ref = uses.partition("@")[2]
                if not ref or ref.lower() in MOVING_REFS:
                    issues.append(f"unpinned:{uses}")
            if "${{ secrets." in str(step.get("run", "")).replace("${{secrets.", "${{ secrets."):
                issues.append(f"secret_in_run:{name}")
            if pr_target and uses and uses.startswith("actions/checkout") and \
                    "github.event.pull_request.head" in str((step.get("with") or {}).get("ref", "")):
                issues.append(f"pr_target_checkout:{name}")
    return issues


# ---------- 6*. Выражения ----------

EXPR = re.compile(r"\$\{\{\s*(.*?)\s*\}\}")


def _lookup(path: str, ctx: dict):
    cur = ctx
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def _eval(expr: str, ctx: dict) -> str:
    for alt in (a.strip() for a in expr.split("||")):
        if len(alt) >= 2 and alt[0] == alt[-1] == "'":
            return alt[1:-1]
        value = _lookup(alt, ctx)
        if value not in (None, "", False):
            return str(value).lower() if isinstance(value, bool) else str(value)
    return ""


def render(text: str, ctx: dict) -> str:
    return EXPR.sub(lambda m: _eval(m.group(1), ctx), text)
