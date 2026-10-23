# Лабораторная 09. Конвейер CI

Агент написал workflow для GitHub Actions, и тот «работает». Но ошибки линтера в нём заглушены, Python 3.10
превратился в 3.1, действия берутся с ветки `main`, а токен деплоя печатается в лог. Сегодня мы:

1. пишем маленький набор инструментов `ci_tools.py`: он читает workflow так же, как GitHub, и находит типичные ошибки;
2. доводим `sample/.github/workflows/ci.yml` до рабочего конвейера и переносим его в проект команды.

```bash
python check.py           # все задачи
python check.py -v 4      # подробности по задаче 4
cd sample && ruff check . && pytest -q   # то же, что будет делать CI
```

## Как GitHub читает workflow

```yaml
on:                 # YAML 1.1: ключ `on` читается как True!
  push:
    branches: [main]
  pull_request:     # значение пустое → None
jobs:
  test:
    needs: lint     # строка или список
    strategy:
      matrix:
        python-version: ["3.12", "3.13"]   # в кавычках! 3.10 без кавычек — это число 3.1
```

## Задачи

| № | Что сделать |
|---|---|
| 1 | `load_workflow(text)`: вернуть ключу `on` его имя (сейчас это `True`); привести `on` к словарю: `push` → `{"push": {}}`, `[push, pull_request]` → два события, `None` в настройках → `{}`. Нет `jobs`, нет `on` или YAML — не словарь → `ValueError`. |
| 2 | `job_order(wf)`: порядок запуска с учётом `needs`. Из готовых первым идёт тот, что раньше в файле. Цикл или ссылка на несуществующий job → `ValueError`. |
| 3 | `expand_matrix(job)`: декартово произведение, затем `exclude` (запись может задавать не все ключи), затем `include` по правилам GitHub (см. docstring). Матрица только из `include` → каждая запись отдельно. |
| 4 | `lint_workflow(wf)`: список замечаний (коды — ниже) в порядке «job за job по файлу; внутри job — `no_permissions`, `no_timeout`, `float_version`, затем шаги по порядку». |
| 5 | `sample/.github/workflows/ci.yml`: события `push` в `main` и `pull_request`; jobs `lint` → `test` → `build`; `ruff check` и `ruff format --check` без `\|\| true`; матрица `"3.12"`, `"3.13"`; `setup-python` с `cache: pip`; `pytest`; `docker build`; `concurrency` с `cancel-in-progress: true`; никаких `secrets.`; `lint_workflow` → `[]`. |
| 6* | `render(text, ctx)`: подставить `${{ matrix.os }}`, `${{ github.event.pull_request.number }}`; нет значения → пустая строка; `a \|\| b \|\| 'строка'` — первое непустое; `True` → `true`. |

### Коды линтера

| Код | Когда | Почему это плохо |
|---|---|---|
| `no_permissions:<job>` | нет `permissions` ни на верхнем уровне, ни у job | токен `GITHUB_TOKEN` получает права по умолчанию — часто на запись |
| `no_timeout:<job>` | нет `timeout-minutes` | зависший тест жжёт минуты до 6 часов |
| `float_version:<job>` | в матрице есть число с точкой | `3.10` превращается в `3.1` |
| `unpinned:<uses>` | у `uses` нет `@ref` или ref — `main`/`master`/`latest`/`HEAD` | чужой коммит в `main` действия сразу попадает в ваш CI. Локальные `./…` и `docker://` не проверяем |
| `secret_in_run:<job>` | в `run` есть `${{ secrets.… }}` | секрет вставляется прямо в текст скрипта; передавайте его через `env:` |
| `pr_target_checkout:<job>` | событие `pull_request_target` и `actions/checkout` с `ref: …github.event.pull_request.head…` | код из чужого форка выполняется с секретами репозитория |

## Проверка у экрана

1. Перенесите `ci.yml` в репозиторий команды (пути к тестам и `requirements.txt` поправьте под проект).
2. Откройте PR, в котором тест специально падает: CI красный, кнопка merge неактивна (включите защиту `main`:
   *Settings → Branches → Require status checks → `lint`, `test`*).
3. Почините тест: CI зелёный, PR одобрен человеком, merge.
