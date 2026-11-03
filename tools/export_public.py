"""Выгрузка материалов курса в открытую репу для учеников ``p58-course-labs``.

Копирует в новую пустую папку только то, что можно показывать ученикам:
уроки недель из диапазона ``--weeks`` (и вводный урок ``w00``), их лабораторные
со стартовым кодом, листы контестов этих уроков (только ``sheet.*``, без решений),
``docs/contest-rules.md``, ``docs/server-windows.md``, ``requirements.txt``, а также генерирует README.md для учеников
``.gitignore`` и ``.github/CODEOWNERS`` (PR в main одобряют только преподаватели).

Никогда не попадают: ``solutions/``, ``rating/``, ``tools/``, ``scripts/``, ``Makefile``,
``docs/labs.md``, ``docs/deck-format.md``, ``notes.md``, кэши и история git.
Из README уроков убираются фрагменты и строки со ссылками на эталоны (``solutions/``, «эталон»),
раздел «Заметки преподавателю» и строки со ссылками на не выгружаемые документы.

После копирования скрипт проверяет результат и печатает отчёт:

* нет путей с ``solutions/`` и ``rating/``;
* в текстовых файлах нет слов «solutions» и «эталон»;
* нет файлов из списка исключений;
* тесты каждой задачи каждой выгруженной лабораторной ПАДАЮТ на стартовом коде
  (стартовый код не должен оказаться решением).

При любом нарушении код возврата ненулевой. Публикация (push) — только вручную, после ревью.

Использование (из корня репозитория курса, нужен pytest в текущем python):

    python tools/export_public.py --weeks 1-1 --out /tmp/p58-export
    python tools/export_public.py --weeks 1-2 --out ../p58-course-labs --git-init --number 2
    python tools/export_public.py --check-only /tmp/p58-export   # только проверки готовой папки

``--git-init`` создаёт в папке выгрузки git-репозиторий с одним коммитом «Выгрузка N»
(без remote; push делает человек после ревью).
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import syllabus as S

# Общая репа для учеников (сдача — своя ветка <ник>/<лаба> в ней и pull request в main).
PUBLIC_REPO = "school58-project/p58-course-labs"
# Слова, которых не должно быть в выгрузке (регистр не важен).
FORBIDDEN_WORDS = ("solutions", "эталон")
# Каталоги, которых не должно быть нигде в пути.
FORBIDDEN_DIRS = ("solutions", "rating")
# Файлы и каталоги курса, которые не выгружаем (пути от корня выгрузки).
EXCLUDED_ROOT = ("tools", "scripts", "Makefile", "docs/labs.md", "docs/deck-format.md")
# Имена файлов и каталогов, которые не выгружаем ни на каком уровне.
EXCLUDED_NAMES = ("notes.md", "__pycache__", ".ruff_cache", ".pytest_cache", ".venv", ".DS_Store", ".env")
EXCLUDED_SUFFIXES = (".pyc",)
# Документы, которые выгружаем всегда.
ROOT_FILES = ("docs/contest-rules.md", "docs/server-windows.md", "requirements.txt")
# Из папки контеста берём только листы с условиями.
CONTEST_FILES = ("sheet.md", "sheet.html", "sheet.pdf")
TEXT_SUFFIXES = {".md", ".py", ".html", ".deck", ".txt", ".ini", ".cfg", ".toml", ".json", ".csv", ".yml",
                 ".yaml", ".sh", ".css", ".js", ""}

GITIGNORE = """\
# окружение и кэши
.venv/
__pycache__/
*.pyc
.ruff_cache/
.pytest_cache/
.env
.DS_Store
"""

# Владельцы кода открытой репы: защита main требует одобрения code owner, то есть преподавателя
# (команда p58-teachers в организации school58-project) — одобрение другого ученика не засчитывается.
CODEOWNERS = """\
# PR в main одобряет преподаватель (команда p58-teachers) или автор курса.
* @school58-project/p58-teachers @TIlzziter
"""


# ---------------------------------------------------------------- выбор файлов

def parse_weeks(text: str) -> tuple[int, int]:
    """«1-2» → (1, 2), «3» → (3, 3)."""
    m = re.fullmatch(r"\s*(\d+)\s*(?:-\s*(\d+))?\s*", text)
    if not m:
        raise argparse.ArgumentTypeError(f"диапазон недель вида 1-2, получено {text!r}")
    a, b = int(m.group(1)), int(m.group(2) or m.group(1))
    if a > b:
        raise argparse.ArgumentTypeError(f"начало диапазона больше конца: {text!r}")
    return a, b


def tracked_files() -> set[str]:
    """Файлы под контролем git (так в выгрузку не попадут кэши и случайные файлы)."""
    res = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, text=True, check=True)
    return {p for p in res.stdout.split("\0") if p}


def is_excluded(rel: str) -> str | None:
    """Причина, по которой путь нельзя выгружать, или None."""
    parts = rel.split("/")
    for d in FORBIDDEN_DIRS:
        if d in parts[:-1] or parts[0] == d:
            return f"путь содержит {d}/"
    for e in EXCLUDED_ROOT:
        if rel == e or rel.startswith(e + "/"):
            return f"исключённый файл {e}"
    for name in parts:
        if name in EXCLUDED_NAMES:
            return f"исключённое имя {name}"
    if rel.endswith(EXCLUDED_SUFFIXES):
        return "кэш"
    return None


def select_lessons(w1: int, w2: int) -> list[tuple[S.Week, S.Lesson]]:
    return [(w, l) for w in S.W if w1 <= w.n <= w2 for l in w.lessons]


def contest_dir(cid: str) -> Path | None:
    found = sorted((ROOT / "contests").glob(f"{cid}-*"))
    return found[0] if found else None


def plan_files(w1: int, w2: int) -> list[str]:
    """Список путей (от корня курса), которые нужно скопировать."""
    tracked = tracked_files()
    dirs = [p.relative_to(ROOT).as_posix() for p in sorted((ROOT / "lessons").glob("w00-*")) if p.is_dir()]
    dirs += [f"lessons/{l.dir}" for _, l in select_lessons(w1, w2)]
    files: list[str] = []
    for d in dirs:
        files += sorted(f for f in tracked if f.startswith(d + "/"))
    for _, l in select_lessons(w1, w2):
        if l.contest and (c := contest_dir(l.contest)):
            rel = c.relative_to(ROOT).as_posix()
            files += [f"{rel}/{n}" for n in CONTEST_FILES if f"{rel}/{n}" in tracked]
    files += [f for f in ROOT_FILES if f in tracked]
    return [f for f in files if not is_excluded(f)]


# ---------------------------------------------------------------- чистка README

SOLUTION_CLAUSE = re.compile(r"\s*[;,]\s*(?:эталон|решения)\s*—\s*`?solutions/[^`\s]*`?", re.IGNORECASE)


RATING_ITEM = re.compile(r"^\* [^\n]*\]\((?:\.\./)*rating/[^\n]*\n(?:[ \t]+[^\n]*\n)*", re.MULTILINE)


def clean_markdown(text: str, removed: list[str]) -> str:
    """Убрать из markdown упоминания решений, заметки преподавателю и ссылки на не выгружаемые документы.

    Сначала вырезается фрагмент «; эталон — `solutions/...`» (остальная строка, например ссылка на лист
    контеста, остаётся). Если строка всё равно упоминает solutions/ или «эталон», она удаляется целиком.
    """
    # Раздел «Заметки преподавателю» (из notes.md) — до конца файла или следующего заголовка ##.
    text = re.sub(r"^## Заметки преподавателю\n.*?(?=^## |\Z)",
                  lambda m: removed.append("раздел «Заметки преподавателю»") or "", text, flags=re.DOTALL | re.MULTILINE)
    # Пункт списка со ссылками на rating/ (таблица рейтинга не выгружается) — заменяем одной строкой.
    text = RATING_ITEM.sub(lambda m: removed.append("пункт со ссылкой на rating/ → «рейтинг ведёт ментор»")
                           or "* Рейтинг ведёт ментор.\n", text)
    out = []
    for line in text.split("\n"):
        new = SOLUTION_CLAUSE.sub("", line)
        if new != line:
            removed.append(f"фрагмент: {line.strip()[:120]}")
        low = new.lower()
        if any(w in low for w in FORBIDDEN_WORDS):
            removed.append(f"строка: {line.strip()[:120]}")
            continue
        if any(f"{e}" in new for e in ("docs/deck-format.md", "docs/labs.md", "](tools/", "](../../tools/",
                                         "](scripts/", "](../../scripts/")):
            removed.append(f"строка со ссылкой на не выгружаемый файл: {line.strip()[:120]}")
            continue
        out.append(new)
    return "\n".join(out).rstrip("\n") + "\n"


# ---------------------------------------------------------------- README для учеников

def student_readme(w1: int, w2: int, number: int, repo: str = PUBLIC_REPO) -> str:
    name = repo.split("/")[-1]
    rows = [f"Уроки по вторникам и пятницам, {S.LESSON_TIME}. ДЗ урока сдаётся до начала следующего урока.", "",
            "| Нед. | Дата | Урок | Тема | ДЗ до | Лабораторная | Контест |", "|---|---|---|---|---|---|---|"]
    w00 = sorted((ROOT / "lessons").glob("w00-*"))
    for d in w00:
        rows.append(f"| 0 | до курса | [00 · Вводный](lessons/{d.name}/README.md) | Как работает сеть (повторение) | | | |")
    for w, l in select_lessons(w1, w2):
        link = f"[{l.num:02d} · {l.kind}](lessons/{l.dir}/README.md)"
        lab = f"[{l.lab.split('-')[0]}](lessons/{l.dir}/labs/{l.lab}/README.md)" if l.lab else ""
        c = contest_dir(l.contest) if l.contest else None
        contest = f"[{l.contest}](contests/{c.name}/sheet.pdf)" if c else ""
        due = S.fmt_day(l.due) if l.due else "—"
        rows.append(f"| {w.n} | {S.fmt_day(l.date)} | {link} | {l.title} | {due} | {lab} | {contest} |")
    weeks = f"неделя {w1}" if w1 == w2 else f"недели {w1}–{w2}"
    return f"""# Проект 58 · 9 класс · материалы для учеников

> {S.WORKING_VERSION}

Здесь лежат материалы курса «Проект 58»: презентации уроков, практические задания и лабораторные
со стартовым кодом и автопроверкой. Материалы добавляются по неделям — перед уроком появляется
следующая неделя. Сейчас выложено: вводный урок 00 и {weeks} (выгрузка {number}).

**Этап 0 (до конца декабря): весь код пишем руками.** Агента можно спрашивать, что значит код
или ошибка, но его код не вставляем.

## Как начать

Работаем на **учебном сервере курса** (логин и адрес выдаёт преподаватель). Начните с
[лабораторной 01](lessons/w01-l02-team-setup/labs/lab01-git-flow/README.md): там по шагам — вход на сервер
и SSH-ключ (шаг 0), клон, своя ветка, решение, `check.py`, коммиты и pull request.
Подробная инструкция для Windows — [`docs/server-windows.md`](docs/server-windows.md):
[первый вход](docs/server-windows.md#1-первый-вход-и-смена-пароля),
[SSH-ключ](docs/server-windows.md#2-создать-ssh-ключ-на-своём-компьютере),
[GitHub на сервере](docs/server-windows.md#5-подключить-github-на-сервере),
[сдача через PR](docs/server-windows.md#6-сдача-домашки-своя-ветка-и-pull-request),
[частые проблемы](docs/server-windows.md#7-частые-проблемы).

Можно и на своём компьютере: нужны Git и Python 3.12 или новее (macOS/Linux; на Windows — WSL или Git Bash).

```bash
# 1. Склонируйте общую репу курса (push — после приглашения от преподавателя)
git clone git@github.com:{repo}.git
cd {name}

# 2. Окружение Python
python3 -m venv .venv
source .venv/bin/activate          # Windows (Git Bash): source .venv/Scripts/activate
python -m pip install -r requirements.txt
```

## Как работать с лабораторной

```bash
cd lessons/w01-l02-team-setup/labs/lab01-git-flow
python check.py          # таблица: какие задачи уже проходят
python check.py -v 3     # подробности по задаче 3
```

Тесты в папке `tests/` не меняйте: при проверке используются тесты из этой репы.

## Как сдавать

Подробно, с примерами экрана — [раздел 6 инструкции](docs/server-windows.md#6-сдача-домашки-своя-ветка-и-pull-request).

Все работают в этой репе, каждый — в своей ветке. В `main` не пушим (она защищена), чужие ветки не трогаем.

1. Возьмите свежие материалы: `git switch main && git pull origin main`.
2. Создайте свою ветку `<ваш-ник>/<лаба>` (ник на GitHub), например `git switch -c <ваш-ник>/lab01`.
3. Делайте небольшие коммиты в формате `область: что сделано`.
4. Запушьте ветку (`git push -u origin <ваш-ник>/lab01`) и откройте pull request в `main`.
   В описании PR — разделы `## Что сделано`, `## Как проверить`, `## Что сгенерировал агент`.
   Новые материалы вышли, пока работали, — `git pull origin main` в своей ветке.
5. Преподаватель запускает тесты по вашему PR и ставит отметку. PR не сливается в основную ветку —
   это просто способ сдать работу.

Не добавляйте в репу пароли, токены, файлы `.env` и личные данные.

## Расписание

<!-- schedule -->
{chr(10).join(rows)}
<!-- /schedule -->

Правила контестов — [`docs/contest-rules.md`](docs/contest-rules.md).
"""


# ---------------------------------------------------------------- выгрузка

def export(w1: int, w2: int, out: Path, number: int, repo: str = PUBLIC_REPO) -> list[str]:
    log: list[str] = []
    files = plan_files(w1, w2)
    for rel in files:
        src, dst = ROOT / rel, out / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix == ".md":
            removed: list[str] = []
            dst.write_text(clean_markdown(src.read_text(encoding="utf-8"), removed), encoding="utf-8")
            log += [f"{rel}: убрано — {r}" for r in removed]
        else:
            shutil.copy2(src, dst)
    (out / "README.md").write_text(student_readme(w1, w2, number, repo), encoding="utf-8")
    (out / ".gitignore").write_text(GITIGNORE, encoding="utf-8")
    (out / ".github").mkdir(exist_ok=True)
    (out / ".github" / "CODEOWNERS").write_text(CODEOWNERS, encoding="utf-8")
    return log


# ---------------------------------------------------------------- проверки

def all_files(out: Path) -> list[str]:
    return sorted(p.relative_to(out).as_posix() for p in out.rglob("*")
                  if p.is_file() and ".git" not in p.relative_to(out).parts)


def run_pytest(files: list[Path], cwd: Path) -> tuple[bool, str]:
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    res = subprocess.run([sys.executable, "-m", "pytest", "-q", "--no-header", "-p", "no:cacheprovider",
                          "--tb=no", *map(str, files)], cwd=cwd, capture_output=True, text=True, env=env,
                         timeout=300, check=False)
    last = (res.stdout.strip().splitlines() or ["нет вывода"])[-1]
    if res.returncode not in (0, 1):
        last = f"код {res.returncode}: {last}"
    return res.returncode == 0, last


def check_lab(lab: Path, out: Path) -> tuple[list[str], list[str]]:
    """Тесты каждой задачи и check.py должны падать на стартовом коде. Запуск — во временной копии."""
    errors, lines = [], []
    rel = lab.relative_to(out).as_posix()
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / lab.name
        shutil.copytree(lab, work)
        tasks: dict[int, list[Path]] = {}
        for f in sorted((work / "tests").glob("test_t*_*.py")):
            tasks.setdefault(int(re.match(r"test_t(\d+)_", f.name).group(1)), []).append(f)
        if not tasks:
            errors.append(f"{rel}: нет тестов tests/test_tN_*.py")
        for n in sorted(tasks):
            ok, last = run_pytest(tasks[n], work)
            mark = "ОШИБКА: проходит на стартовом коде" if ok else "падает — OK"
            lines.append(f"    задача t{n}: {mark} ({last})")
            if ok:
                errors.append(f"{rel}: задача {n} проходит на стартовом коде ({last})")
        if (work / "check.py").exists():
            env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
            res = subprocess.run([sys.executable, "check.py"], cwd=work, capture_output=True, text=True, env=env,
                                 timeout=600, check=False)
            tail = (res.stdout.strip().splitlines() or ["нет вывода"])
            done = next((s for s in tail if s.startswith("Готово задач")), tail[-1])
            lines.append(f"    check.py: код возврата {res.returncode}, «{done}»")
            if res.returncode == 0:
                errors.append(f"{rel}: check.py завершился успешно на стартовом коде")
        else:
            errors.append(f"{rel}: нет check.py")
    return errors, lines


def github_anchors(text: str) -> set[str]:
    """Якоря заголовков markdown так, как их строит GitHub: нижний регистр, без знаков препинания, пробел → «-»."""
    anchors: set[str] = set()
    seen: dict[str, int] = {}
    fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fence = not fence
            continue
        m = None if fence else re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not m:
            continue
        title = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", m.group(1))       # [текст](ссылка) → текст
        slug = re.sub(r"[^\w\- ]", "", title.lower()).replace(" ", "-")
        n = seen.get(slug, 0)
        seen[slug] = n + 1
        anchors.add(slug if n == 0 else f"{slug}-{n}")
    anchors |= set(re.findall(r'<a\s+(?:id|name)="([^"]+)"', text))
    return anchors


def check_links(out: Path) -> list[str]:
    """Относительные ссылки в .md, ведущие на несуществующие файлы или якоря (предупреждения)."""
    warns = []
    cache: dict[Path, set[str]] = {}
    for rel in all_files(out):
        if not rel.endswith(".md"):
            continue
        p = out / rel
        for target in re.findall(r"\]\(([^)\s]+)\)", p.read_text(encoding="utf-8")):
            if re.match(r"[a-z]+:", target):
                continue
            path, _, anchor = target.partition("#")
            t = (p.parent / path).resolve() if path else p.resolve()
            if not t.exists():
                warns.append(f"{rel}: ссылка на отсутствующий файл {target}")
                continue
            if anchor and t.suffix == ".md":
                if t not in cache:
                    cache[t] = github_anchors(t.read_text(encoding="utf-8"))
                if anchor.lower() not in cache[t]:
                    warns.append(f"{rel}: в {path or rel} нет раздела #{anchor}")
    return warns


def self_check(out: Path) -> int:
    files = all_files(out)
    errors: list[str] = []
    print(f"\nПроверка выгрузки {out}: файлов {len(files)}")

    bad_paths = [f for f in files if any(d in f.split("/")[:-1] for d in FORBIDDEN_DIRS)]
    errors += [f"путь с solutions/ или rating/: {f}" for f in bad_paths]
    print(f"  [{'OK' if not bad_paths else 'ОШИБКА'}] нет путей с solutions/ и rating/")

    excluded = [(f, r) for f in files if (r := is_excluded(f))]
    errors += [f"исключённый файл в выгрузке: {f} ({r})" for f, r in excluded]
    print(f"  [{'OK' if not excluded else 'ОШИБКА'}] нет исключённых файлов "
          "(tools/, scripts/, Makefile, docs/labs.md, docs/deck-format.md, notes.md, кэши)")

    hits, skipped = [], []
    for f in files:
        p = out / f
        if p.suffix.lower() not in TEXT_SUFFIXES:
            skipped.append(f)
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            skipped.append(f)
            continue
        for i, line in enumerate(text.splitlines(), 1):
            low = line.lower()
            for w in FORBIDDEN_WORDS:
                if w in low:
                    hits.append(f"{f}:{i}: «{w}»")
    errors += [f"запрещённое слово: {h}" for h in hits]
    print(f"  [{'OK' if not hits else 'ОШИБКА'}] нет слов «solutions» и «эталон» в текстовых файлах"
          f" (проверено {len(files) - len(skipped)}, не текст: {', '.join(skipped) or '—'})")

    for need in ("README.md", ".gitignore", ".github/CODEOWNERS"):
        if need not in files:
            errors.append(f"нет {need}")

    labs = sorted({str(Path(f).parent.parent) for f in files if re.search(r"/labs/[^/]+/tests/test_t\d+_", f)})
    labs = [out / p for p in labs]
    print(f"  Лабораторные ({len(labs)}): тесты на стартовом коде должны падать")
    for lab in labs:
        errs, lines = check_lab(lab, out)
        print(f"  [{'OK' if not errs else 'ОШИБКА'}] {lab.relative_to(out)}")
        for s in lines:
            print(s)
        errors += errs

    warns = check_links(out)
    if warns:
        print("  Предупреждения (битые ссылки):")
        for w in warns:
            print("   -", w)
    else:
        print("  [OK] относительные ссылки в .md ведут на существующие файлы")

    print()
    if errors:
        print("НАРУШЕНИЯ:")
        for e in errors:
            print(" -", e)
        return 1
    print("Проверка пройдена: нарушений нет.")
    return 0


def git_init(out: Path, number: int) -> None:
    def git(*args):
        subprocess.run(["git", *args], cwd=out, check=True, capture_output=True, text=True)
    git("init", "-q", "-b", "main")
    git("add", "-A")
    ident = []
    if not subprocess.run(["git", "config", "user.name"], cwd=out, capture_output=True, text=True,
                          check=False).stdout.strip():
        ident = ["-c", "user.name=Project 58", "-c", "user.email=p58@example.invalid"]
    subprocess.run(["git", *ident, "commit", "-q", "-m", f"Выгрузка {number}"], cwd=out, check=True)
    print(f"git: создан репозиторий в {out}, один коммит «Выгрузка {number}», remote не задан.")


def main() -> int:
    ap = argparse.ArgumentParser(description="Выгрузка материалов курса для учеников (без решений).")
    ap.add_argument("--weeks", type=parse_weeks, help="диапазон недель, например 1-1 или 1-2 (урок w00 — всегда)")
    ap.add_argument("--out", type=Path, help="новая пустая папка для выгрузки")
    ap.add_argument("--number", type=int, default=1, help="номер выгрузки для README и коммита (по умолчанию 1)")
    ap.add_argument("--repo", default=PUBLIC_REPO,
                    help=f"открытая репа для README учеников, OWNER/NAME (по умолчанию {PUBLIC_REPO})")
    ap.add_argument("--git-init", action="store_true", help="сделать в папке git-репозиторий с коммитом «Выгрузка N»")
    ap.add_argument("--check-only", type=Path, metavar="DIR", help="только проверить готовую папку выгрузки")
    args = ap.parse_args()

    if args.check_only:
        return self_check(args.check_only.resolve())
    if not args.weeks or not args.out:
        ap.error("нужны --weeks и --out (или --check-only DIR)")
    out = args.out.resolve()
    if out.exists() and any(out.iterdir()):
        print(f"Папка {out} уже существует и не пуста — выберите новую.", file=sys.stderr)
        return 2
    if out == ROOT or ROOT in out.parents:
        print("Папка выгрузки не должна быть внутри репозитория курса.", file=sys.stderr)
        return 2
    w1, w2 = args.weeks
    out.mkdir(parents=True, exist_ok=True)
    log = export(w1, w2, out, args.number, args.repo)
    print(f"Выгрузка недель {w1}–{w2} (+ w00) в {out}")
    for f in all_files(out):
        print("  ", f)
    if log:
        print("Правки при выгрузке:")
        for s in log:
            print("  -", s)
    rc = self_check(out)
    if rc == 0 and args.git_init:
        git_init(out, args.number)
    elif args.git_init:
        print("git-репозиторий не создан: есть нарушения.")
    return rc


if __name__ == "__main__":
    sys.exit(main())
