"""Ревью Docker- и Nginx-конфигов по чек-листу DevOps.

Агент сгенерировал Dockerfile и docker-compose.yml (см. examples/*.agent*). Вместо того чтобы проверять их
«на глаз», пишем автоматическое ревью: каждая проблема — код из списка в README.md.
Этот модуль потом можно запускать в CI на каждый PR, который меняет конфиги.
"""
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
    result = []
    for line in text.splitlines():
        if line.startswith("#"):
            continue
        instr, _, args = line.partition(" ")
        result.append((instr, args))
    return result


# ---------- задача 2 ----------
def dockerfile_problems(text: str) -> list[str]:
    """Коды: no_base_tag, root_user, copy_before_deps, pip_cache, secret_in_env (в этом порядке)."""
    problems = []
    for instr, args in parse_dockerfile(text):
        if instr == "FROM" and args.endswith(":latest"):
            problems.append("no_base_tag")
    # TODO: root_user, copy_before_deps, pip_cache, secret_in_env
    return problems


# ---------- задача 3 ----------
def compose_problems(text: str) -> list[str]:
    """Коды без повторов, в порядке обнаружения: db_port_public, secret_in_compose, no_restart,
    no_healthcheck, unknown_dependency."""
    raise NotImplementedError("задача 3")


# ---------- задача 4 ----------
def start_order(text: str) -> list[str]:
    """Порядок запуска сервисов по depends_on; при равенстве — по алфавиту. Цикл — ValueError."""
    raise NotImplementedError("задача 4")


# ---------- задача 5 ----------
def proxy_targets(conf: str) -> dict[str, str]:
    """location → адрес из proxy_pass (без схемы и пути): {"/api/": "app:8000"}."""
    raise NotImplementedError("задача 5")


def nginx_problems(conf: str, compose_text: str) -> list[str]:
    """["unknown_upstream"], если proxy_pass ведёт на хост, которого нет среди сервисов compose и upstream-ов."""
    raise NotImplementedError("задача 5")


# ---------- задача 6 ----------
REQUIRED_IGNORE = (".env", ".git", ".venv", "__pycache__")


def dockerignore_missing(text: str) -> list[str]:
    """Каких строк из REQUIRED_IGNORE не хватает (в порядке REQUIRED_IGNORE)."""
    raise NotImplementedError("задача 6")


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
    """Markdown-отчёт для комментария к PR (формат — в README.md)."""
    raise NotImplementedError("задача 7")
