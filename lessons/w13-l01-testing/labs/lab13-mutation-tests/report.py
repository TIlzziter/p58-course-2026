"""Отчёт по мутантам: python report.py [модуль]. Показывает, кто выжил."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "tests"))
from grader import run_suite  # noqa: E402
from mutants import MUTANTS  # noqa: E402


def main():
    only = sys.argv[1:]
    for module, ms in MUTANTS.items():
        if only and module not in only:
            continue
        ok, last = run_suite(module)
        if not ok:
            print(f"{module:<11} ваши тесты падают на правильном коде: {last}")
            continue
        alive = [m[0] for m in ms if run_suite(module, m)[0]]
        print(f"{module:<11} убито {len(ms) - len(alive)} из {len(ms)}" + (f"; выжили: {', '.join(alive)}" if alive else ""))


if __name__ == "__main__":
    main()
