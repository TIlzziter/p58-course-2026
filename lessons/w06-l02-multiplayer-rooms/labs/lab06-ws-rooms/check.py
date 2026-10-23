"""Автопроверка лабораторной: запускает тесты каждой задачи и печатает таблицу.

Запуск из папки лабораторной:  python check.py        — все задачи
                               python check.py 3      — только задача 3
                               python check.py -v 3   — подробный вывод pytest
"""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def tasks():
    found = {}
    for f in sorted((HERE / "tests").glob("test_t*_*.py")):
        n = int(re.match(r"test_t(\d+)_", f.name).group(1))
        found.setdefault(n, []).append(f)
    return found


def main():
    args = sys.argv[1:]
    verbose = "-v" in args
    only = {int(a) for a in args if a.isdigit()}
    rows = []
    for n, files in tasks().items():
        if only and n not in only:
            continue
        cmd = [sys.executable, "-m", "pytest", "-q", "--no-header", "-p", "no:cacheprovider", *map(str, files)]
        if not verbose:
            cmd += ["--tb=line"]
        res = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True)
        ok = res.returncode == 0
        summary = (res.stdout.strip().splitlines() or ["нет вывода"])[-1]
        rows.append((n, ok, summary))
        if verbose or (only and not ok):
            print(res.stdout[-4000:], res.stderr[-2000:])
    print()
    print("Задача  Статус  Итог pytest")
    for n, ok, summary in rows:
        print(f"{n:>6}  {'  OK ' if ok else ' НЕТ '}  {summary}")
    done = sum(ok for _, ok, _ in rows)
    print(f"\nГотово задач: {done} из {len(rows)}")
    if done < len(rows):
        print("Подробности по задаче N: python check.py -v N")
    return 0 if done == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
