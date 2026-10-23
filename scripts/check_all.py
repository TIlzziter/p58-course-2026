"""Проверка всего курса.

1. Каждая лабораторная: тесты каждой задачи ПАДАЮТ на стартовом коде
   и ВСЕ тесты ПРОХОДЯТ, если наложить эталон из solutions/labs/<lab>/.
2. Каждый контест: эталонные решения из solutions/contests/<contest>/ проходят свои тесты.
3. Каждый урок: есть README.md и собранная презентация, .deck и .html совпадают.

Запуск из корня репозитория:  python scripts/check_all.py [--only lab01,c02]
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable
sys.path.insert(0, str(ROOT / "tools"))


def pytest(paths, cwd) -> tuple[bool, str]:
    res = subprocess.run([PY, "-m", "pytest", "-q", "--no-header", "-p", "no:cacheprovider", "--tb=short", *map(str, paths)],
                         cwd=cwd, capture_output=True, text=True, timeout=600)
    last = (res.stdout.strip().splitlines() or ["?"])[-1]
    return res.returncode == 0, last if res.returncode in (0, 1) else res.stdout[-1500:] + res.stderr[-1500:]


def check_lab(lab: Path) -> list[str]:
    errors = []
    sol = ROOT / "solutions" / "labs" / lab.name
    if not sol.is_dir():
        return [f"{lab.name}: нет эталона {sol.relative_to(ROOT)}"]
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / lab.name
        shutil.copytree(lab, work)
        tasks: dict[int, list[Path]] = {}
        for f in sorted((work / "tests").glob("test_t*_*.py")):
            tasks.setdefault(int(re.match(r"test_t(\d+)_", f.name).group(1)), []).append(f)
        if not tasks:
            errors.append(f"{lab.name}: нет тестов tests/test_tN_*.py")
        for n, files in tasks.items():
            ok, last = pytest(files, work)
            if ok:
                errors.append(f"{lab.name}: задача {n} проходит на стартовом коде ({last})")
        shutil.copytree(sol, work, dirs_exist_ok=True)
        ok, last = pytest([work / "tests"], work)
        if not ok:
            errors.append(f"{lab.name}: эталон не проходит тесты: {last}")
        status = "OK" if not errors else "ОШИБКА"
        print(f"  {lab.name:<32} задач: {len(tasks):>2}  стартовый код падает, эталон: {last}  [{status}]")
    return errors


def check_contest(sol: Path) -> list[str]:
    ok, last = pytest([sol], sol)
    print(f"  {sol.name:<32} эталон: {last}  [{'OK' if ok else 'ОШИБКА'}]")
    return [] if ok else [f"{sol.name}: {last}"]


def check_lessons() -> list[str]:
    import deck
    import syllabus
    errors = []
    for lesson in syllabus.LESSONS:
        d = ROOT / "lessons" / lesson.dir
        if not d.is_dir():
            errors.append(f"нет папки урока {lesson.dir}")
            continue
        if not (d / "README.md").exists():
            errors.append(f"{lesson.dir}: нет README.md")
        src = d / f"{lesson.deck}.deck"
        html = d / f"{lesson.deck}.html"
        if not src.exists() or not html.exists():
            errors.append(f"{lesson.dir}: нет {lesson.deck}.deck/.html")
            continue
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "x.html"
            n = deck.build(src, out)
            if out.read_text(encoding="utf-8") != html.read_text(encoding="utf-8"):
                errors.append(f"{lesson.dir}: {html.name} устарел — запустите make decks")
        if lesson.lab and not (d / "labs" / lesson.lab).is_dir():
            errors.append(f"{lesson.dir}: нет лабораторной {lesson.lab}")
        if lesson.part == 1 and n < 18:
            errors.append(f"{lesson.dir}: в лекции всего {n} слайдов")
    print(f"  уроков в расписании: {len(syllabus.LESSONS)}, ошибок: {len(errors)}")
    return errors


def main() -> int:
    only = set()
    if "--only" in sys.argv:
        only = set(sys.argv[sys.argv.index("--only") + 1].split(","))
    errors: list[str] = []
    labs = sorted(ROOT.glob("lessons/*/labs/lab*"), key=lambda p: p.name)
    print(f"Лабораторные ({len(labs)}):")
    for lab in labs:
        if not only or lab.name.split("-")[0] in only:
            errors += check_lab(lab)
    contests = sorted(p for p in (ROOT / "solutions" / "contests").glob("c*") if p.is_dir())
    print(f"Контесты ({len(contests)}):")
    for c in contests:
        if not only or c.name.split("-")[0] in only:
            errors += check_contest(c)
    if not only:
        print("Уроки:")
        errors += check_lessons()
    print()
    if errors:
        print("ОШИБКИ:")
        for e in errors:
            print(" -", e)
        return 1
    print("Всё в порядке.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
