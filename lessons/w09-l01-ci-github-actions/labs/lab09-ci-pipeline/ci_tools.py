"""Инструменты для GitHub Actions: загрузка, порядок jobs, матрица, линтер, подстановка выражений.

Задачи 1–4 и 6 — здесь. Задача 5 — файл sample/.github/workflows/ci.yml.
Код написан «агентом» и работает только на простых примерах. Найдите и исправьте ошибки.
"""
import itertools
import re

import yaml

# ---------- 1. Загрузка ----------


def load_workflow(text: str) -> dict:
    """Читает workflow. Возвращает словарь, где wf["on"] — всегда dict «событие → настройки» (без None).

    Нет jobs или on, или это вообще не словарь → ValueError.
    """
    # TODO: проверьте, что yaml.safe_load делает с ключом `on`. Подсказка: YAML 1.1, «Norway problem».
    return yaml.safe_load(text)


# ---------- 2. Порядок jobs ----------


def job_order(wf: dict) -> list[str]:
    """Порядок запуска jobs с учётом needs (строка или список).

    Из готовых к запуску первым берём тот, что раньше в файле. Цикл или неизвестный job → ValueError.
    """
    return list(wf["jobs"])


# ---------- 3. Матрица ----------


def expand_matrix(job: dict) -> list[dict]:
    """Все комбинации strategy.matrix в порядке itertools.product, затем exclude, затем include.

    Правила include — как в GitHub: запись дописывает новые ключи во все комбинации, совпадающие с ней
    по исходным ключам матрицы; если не подошла ни к одной — становится отдельной комбинацией.
    Нет матрицы → [{}].
    """
    matrix = (job.get("strategy") or {}).get("matrix")
    if not matrix:
        return [{}]
    keys = list(matrix)
    return [dict(zip(keys, values)) for values in itertools.product(*(matrix[k] for k in keys))]


# ---------- 4. Линтер ----------


def lint_workflow(wf: dict) -> list[str]:
    """Список замечаний в порядке: jobs по файлу, внутри job — сначала свойства job, потом шаги.

    Коды: no_permissions:<job>, no_timeout:<job>, float_version:<job>, unpinned:<uses>,
    secret_in_run:<job>, pr_target_checkout:<job>. Подробности — в README.
    """
    issues = []
    for job in wf["jobs"].values():
        for step in job.get("steps") or []:
            uses = step.get("uses")
            if uses and "@" not in uses:
                issues.append(f"unpinned:{uses}")
    return issues


# ---------- 6*. Выражения ----------

EXPR = re.compile(r"\$\{\{\s*(.*?)\s*\}\}")


def render(text: str, ctx: dict) -> str:
    """Подставляет ${{ a.b.c }} из ctx; поддерживает `||` и строки в одинарных кавычках."""
    raise NotImplementedError
