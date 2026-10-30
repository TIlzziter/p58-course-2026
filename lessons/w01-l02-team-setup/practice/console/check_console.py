"""Самопроверка практики «Консоль и Git руками» (урок 02).

Запуск:  python check_console.py ПУТЬ_К_РАБОЧЕЙ_ПАПКЕ
Пример:  python check_console.py ~/p58-console

Печатает по каждому заданию OK или НЕТ и подсказку, чего не хватает.
Зависимостей нет: нужен только Python 3.8+ (и git для задания 6).
"""
from __future__ import annotations

import glob
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

TREE = ["project/frontend", "project/backend", "project/logic", "project/docs/notes", "sandbox"]
HELLO_ARG = "p58-proverka"


def run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str]:
    try:
        res = subprocess.run(cmd, check=False, cwd=cwd, capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.TimeoutExpired) as e:
        return 1, str(e)
    return res.returncode, (res.stdout + res.stderr).strip()


def t1_tree(w: Path) -> tuple[bool, str]:
    missing = [d for d in TREE if not (w / d).is_dir()]
    return (not missing, "все папки на месте" if not missing else "нет папок: " + ", ".join(missing))


def t2_files(w: Path) -> tuple[bool, str]:
    s = w / "sandbox"
    problems = []
    if not (s / "notes.txt").is_file():
        problems.append("нет sandbox/notes.txt (cp + mv)")
    for extra in ("draft.txt", "copy.txt"):
        if (s / extra).exists():
            problems.append(f"sandbox/{extra} не удалён (mv / rm)")
    return (not problems, "notes.txt есть, лишнее удалено" if not problems else "; ".join(problems))


def t3_streams(w: Path) -> tuple[bool, str]:
    f = w / "sandbox" / "todo.txt"
    if not f.is_file():
        return False, "нет sandbox/todo.txt (grep ... > sandbox/todo.txt)"
    lines = [x.strip() for x in f.read_text(encoding="utf-8", errors="replace").splitlines() if x.strip()]
    todo = [x for x in lines if "TODO" in x]
    if not todo:
        return False, "в todo.txt нет строк с TODO"
    if not lines or not lines[-1].isdigit():
        return False, "последняя строка todo.txt — не число (... | wc -l >> sandbox/todo.txt)"
    if int(lines[-1]) != len(todo):
        return False, f"в конце записано {lines[-1]}, а строк с TODO {len(todo)}"
    return True, f"найдено TODO: {len(todo)}"


def t4_script(w: Path) -> tuple[bool, str]:
    f = w / "hello.sh"
    if not f.is_file():
        return False, "нет hello.sh в рабочей папке"
    if os.name == "nt":
        if not shutil.which("bash"):
            return False, "нет bash: запустите проверку из Git Bash или WSL"
        cmd = ["bash", str(f), HELLO_ARG]
    else:
        if not os.access(f, os.X_OK):
            return False, "hello.sh нельзя запустить: chmod +x hello.sh"
        cmd = [str(f), HELLO_ARG]
    code, out = run(cmd, cwd=w)
    if code != 0:
        return False, f"hello.sh завершился с ошибкой: {out[:120]}"
    if HELLO_ARG not in out:
        return False, f"hello.sh {HELLO_ARG} не напечатал аргумент (используйте $1)"
    return True, "запускается и печатает аргумент"


def t5_env(w: Path) -> tuple[bool, str]:
    f = w / "env.txt"
    if not f.is_file():
        return False, "нет env.txt"
    text = f.read_text(encoding="utf-8", errors="replace")
    problems = []
    if not re.search(r"[/\\]\S*python", text, re.IGNORECASE):
        problems.append("нет пути к python (which python)")
    if not re.search(r"Python 3\.\d+", text):
        problems.append("нет версии Python 3 (python --version)")
    if not re.search(r"^P58_NICK=\S+", text, re.MULTILINE):
        problems.append("нет строки P58_NICK=<ник> (export и echo)")
    return (not problems, "путь, версия и переменная есть" if not problems else "; ".join(problems))


def find_repo(w: Path) -> Path | None:
    preferred = w / "p58-course-labs"
    if (preferred / ".git").exists():
        return preferred
    for d in sorted(w.iterdir()):
        if d.is_dir() and (d / ".git").exists():
            return d
    return None


def t6_git(w: Path) -> tuple[bool, str]:
    if not shutil.which("git"):
        return False, "git не установлен"
    repo = find_repo(w)
    if repo is None:
        return False, "в рабочей папке нет склонированного репозитория (git clone ...)"
    problems = []
    for key in ("user.name", "user.email"):
        if run(["git", "config", key], cwd=repo)[0] != 0:
            problems.append(f"не задан git config {key}")
    code, branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo)
    if code != 0 or branch in ("main", "master", "HEAD"):
        problems.append(f"текущая ветка «{branch}» — создайте свою (git switch -c ...)")
    code, files = run(["git", "ls-tree", "-r", "--name-only", "HEAD"], cwd=repo)
    if not any(re.fullmatch(r"about-[\w.-]+\.md", Path(p).name) for p in files.splitlines()):
        problems.append("в последнем коммите нет файла about-<ник>.md (git add + git commit)")
    return (not problems, f"{repo.name}: ветка {branch}, about-*.md закоммичен" if not problems else "; ".join(problems))


def t7_venv(w: Path) -> tuple[bool, str]:
    repo = find_repo(w)
    places = [w / ".venv"] + ([repo / ".venv"] if repo else [])
    venv = next((p for p in places if (p / "pyvenv.cfg").is_file()), None)
    if venv is None:
        return False, "нет .venv (python -m venv .venv в рабочей папке)"
    site = glob.glob(str(venv / "lib" / "python*" / "site-packages" / "pytest")) + \
        glob.glob(str(venv / "Lib" / "site-packages" / "pytest"))
    if not site:
        return False, f"{venv.relative_to(w)} есть, но pytest не установлен (pip install -r requirements.txt)"
    return True, f"{venv.relative_to(w)} с зависимостями курса; вывод python check.py покажите ментору"


def t8_ssh(w: Path) -> tuple[bool | None, str]:
    keys = glob.glob(str(Path.home() / ".ssh" / "id_*.pub"))
    return (True, "публичный ключ есть; добавлен ли он в GitHub — проверьте сами") if keys else (None, "бонус, дома")


TASKS = [
    ("Навигация: дерево папок", t1_tree),
    ("Файлы: cp, mv, rm", t2_files),
    ("Потоки: grep, wc -l", t3_streams),
    ("Права и скрипт hello.sh", t4_script),
    ("Окружение: env.txt", t5_env),
    ("Git: ветка и коммит about-<ник>.md", t6_git),
    ("Python-окружение .venv", t7_venv),
    ("Бонус: SSH-ключ", t8_ssh),
]


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.strip())
        return 2
    w = Path(argv[1]).expanduser().resolve()
    if not w.is_dir():
        print(f"Папка не найдена: {w}")
        return 2
    print(f"Рабочая папка: {w}\n")
    done = 0
    for i, (name, fn) in enumerate(TASKS, 1):
        try:
            ok, hint = fn(w)
        except Exception as e:  # noqa: BLE001 — самопроверка не должна падать на необычной папке
            ok, hint = False, f"ошибка проверки: {e}"
        mark = "OK " if ok else ("—  " if ok is None else "НЕТ")
        print(f"{i}. {name:<38} {mark}  {hint}")
        if ok and i <= 7:
            done += 1
    print(f"\nИтого: {done} из 7 обязательных заданий.")
    return 0 if done == 7 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
