"""Ревью Docker- и Nginx-конфигов по чек-листу DevOps (эталон)."""
import re

import yaml

SECRET_WORDS = ("TOKEN", "PASSWORD", "SECRET", "API_KEY")
SEVERITY = {"secret_in_env": 1, "secret_in_compose": 1, "db_port_public": 1, "root_user": 2,
            "no_base_tag": 2, "copy_before_deps": 3, "pip_cache": 3, "no_restart": 3,
            "no_healthcheck": 3, "unknown_dependency": 1, "unknown_upstream": 1, "dockerignore_missing": 2}


# ---------- задача 1 ----------
def parse_dockerfile(text: str) -> list[tuple[str, str]]:
    """Инструкции Dockerfile: [("FROM", "python:3.12-slim"), ...]. Комментарии и пустые строки пропускаем,
    строки с \\ в конце склеиваем через пробел, имя инструкции — в верхнем регистре."""
    result, buf = [], ""
    for raw in text.splitlines():
        line = raw.strip()
        if not buf and (not line or line.startswith("#")):
            continue
        if line.endswith("\\"):
            buf += line[:-1].strip() + " "
            continue
        line = (buf + line).strip()
        buf = ""
        if not line:
            continue
        instr, _, args = line.partition(" ")
        result.append((instr.upper(), args.strip()))
    if buf.strip():
        instr, _, args = buf.strip().partition(" ")
        result.append((instr.upper(), args.strip()))
    return result


# ---------- задача 2 ----------
def dockerfile_problems(text: str) -> list[str]:
    instrs = parse_dockerfile(text)
    problems = []
    froms = [a for i, a in instrs if i == "FROM"]
    if froms:
        image = froms[-1].split()[0]
        name_tag = image.rsplit("/", 1)[-1]
        if ":" not in name_tag or name_tag.endswith(":latest"):
            problems.append("no_base_tag")
    users = [a for i, a in instrs if i == "USER"]
    if not users or users[-1].split(":")[0] in ("root", "0"):
        problems.append("root_user")
    copy_all = next((n for n, (i, a) in enumerate(instrs) if i in ("COPY", "ADD") and re.match(r"^\.\s+\S", a)), None)
    pip = next((n for n, (i, a) in enumerate(instrs) if i == "RUN" and "pip install" in a), None)
    if copy_all is not None and pip is not None and copy_all < pip:
        problems.append("copy_before_deps")
    if any(i == "RUN" and "pip install" in a and "--no-cache-dir" not in a for i, a in instrs):
        problems.append("pip_cache")
    for i, a in instrs:
        if i in ("ENV", "ARG"):
            names = (re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\s*=", a) or [a.split()[0]]) if a else []
            if any(w in n.upper() for n in names for w in SECRET_WORDS):
                problems.append("secret_in_env")
                break
    return problems


# ---------- задача 3 ----------
def compose_problems(text: str) -> list[str]:
    data = yaml.safe_load(text) or {}
    services = data.get("services", {}) or {}
    problems: list[str] = []

    def add(code):
        if code not in problems:
            problems.append(code)

    for name, svc in services.items():
        svc = svc or {}
        image = str(svc.get("image", ""))
        is_db = name in ("db", "postgres", "redis") or image.startswith(("postgres", "redis"))
        for p in svc.get("ports", []) or []:
            p = str(p)
            parts = p.split(":")
            if is_db and not (len(parts) == 3 and parts[0] in ("127.0.0.1", "localhost")):
                add("db_port_public")
        env = svc.get("environment", {}) or {}
        items = env.items() if isinstance(env, dict) else (e.partition("=")[::2] for e in env)
        for k, v in items:
            if any(w in str(k).upper() for w in SECRET_WORDS) and v not in (None, "") and not str(v).startswith("${"):
                add("secret_in_compose")
        if "restart" not in svc:
            add("no_restart")
        if is_db and "healthcheck" not in svc:
            add("no_healthcheck")
        deps = svc.get("depends_on", []) or []
        for d in (deps.keys() if isinstance(deps, dict) else deps):
            if d not in services:
                add("unknown_dependency")
    return problems


# ---------- задача 4 ----------
def start_order(text: str) -> list[str]:
    """Порядок запуска сервисов по depends_on; при равенстве — по алфавиту. Цикл — ValueError."""
    services = (yaml.safe_load(text) or {}).get("services", {}) or {}
    deps = {}
    for name, svc in services.items():
        d = (svc or {}).get("depends_on", []) or []
        deps[name] = set(d.keys() if isinstance(d, dict) else d) & set(services)
    order: list[str] = []
    while deps:
        ready = sorted(n for n, d in deps.items() if not d)
        if not ready:
            raise ValueError("цикл в depends_on: " + ", ".join(sorted(deps)))
        n = ready[0]
        order.append(n)
        del deps[n]
        for d in deps.values():
            d.discard(n)
    return order


# ---------- задача 5 ----------
def proxy_targets(conf: str) -> dict[str, str]:
    """location → адрес из proxy_pass (без схемы и пути): {"/api/": "app:8000"}."""
    result = {}
    conf = re.sub(r"#.*", "", conf)
    for m in re.finditer(r"location\s+(?:[=~^*]+\s+)?(\S+)\s*\{([^}]*)\}", conf):
        p = re.search(r"proxy_pass\s+https?://([^/;\s]+)", m.group(2))
        if p:
            result[m.group(1)] = p.group(1)
    return result


def nginx_problems(conf: str, compose_text: str) -> list[str]:
    services = set(((yaml.safe_load(compose_text) or {}).get("services") or {}).keys())
    upstreams = set(re.findall(r"upstream\s+(\S+)\s*\{", conf))
    for target in proxy_targets(conf).values():
        host = target.split(":")[0]
        if host not in services and host not in upstreams:
            return ["unknown_upstream"]
    return []


# ---------- задача 6 ----------
REQUIRED_IGNORE = (".env", ".git", ".venv", "__pycache__")


def dockerignore_missing(text: str) -> list[str]:
    lines = {ln.strip().rstrip("/").removeprefix("**/").removeprefix("/") for ln in text.splitlines()
             if ln.strip() and not ln.strip().startswith("#")}
    return [x for x in REQUIRED_IGNORE if x not in lines]


# ---------- задача 7* ----------
MESSAGES = {
    "secret_in_env": "Секрет в ENV/ARG Dockerfile — он останется в слоях образа",
    "secret_in_compose": "Секрет прямо в docker-compose.yml — используйте env_file или ${VAR}",
    "db_port_public": "Порт базы открыт наружу — уберите ports или привяжите к 127.0.0.1",
    "unknown_dependency": "depends_on ссылается на несуществующий сервис",
    "unknown_upstream": "proxy_pass ведёт на хост, которого нет в compose",
    "root_user": "Контейнер работает от root — добавьте USER",
    "no_base_tag": "Базовый образ без конкретной версии",
    "dockerignore_missing": "В .dockerignore не хватает обязательных строк",
    "copy_before_deps": "COPY . . до установки зависимостей — кэш слоёв не работает",
    "pip_cache": "pip install без --no-cache-dir — образ больше, чем нужно",
    "no_restart": "У сервиса нет restart-политики",
    "no_healthcheck": "У базы нет healthcheck",
}


def report(dockerfile: str, compose: str, nginx: str, dockerignore: str) -> str:
    codes = dockerfile_problems(dockerfile) + compose_problems(compose) + nginx_problems(nginx, compose)
    if dockerignore_missing(dockerignore):
        codes.append("dockerignore_missing")
    codes = sorted(set(codes), key=lambda c: (SEVERITY[c], c))
    if not codes:
        return "## Ревью конфигов\n\nЗамечаний нет ✅\n"
    lines = ["## Ревью конфигов", ""]
    for c in codes:
        mark = "🔴" if SEVERITY[c] == 1 else "🟡" if SEVERITY[c] == 2 else "⚪"
        lines.append(f"- [ ] {mark} `{c}` — {MESSAGES[c]}")
    lines.append("")
    lines.append(f"Итого: {len(codes)}, критичных: {sum(SEVERITY[c] == 1 for c in codes)}")
    return "\n".join(lines) + "\n"
