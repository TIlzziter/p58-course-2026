"""Запуск ваших тестов из mytests/ на исходном коде и на мутантах."""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

LAB = Path(__file__).resolve().parent.parent
TIMEOUT = 30


def run_suite(module: str, mutant: tuple[str, str, str] | None = None) -> tuple[bool, str]:
    """True, если mytests/test_<module>.py проходит на коде (с наложенным мутантом)."""
    suite = LAB / "mytests" / f"test_{module}.py"
    if not suite.exists():
        return False, f"нет файла {suite.relative_to(LAB)}"
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        shutil.copytree(LAB / "game", work / "game")
        shutil.copytree(LAB / "mytests", work / "mytests")
        shutil.copy(LAB / "pytest.ini", work / "pytest.ini")
        if mutant:
            src = work / "game" / f"{module}.py"
            code = src.read_text(encoding="utf-8")
            _, old, new = mutant
            assert code.count(old) == 1, f"мутант не применился: {old!r} — game/{module}.py изменён?"
            src.write_text(code.replace(old, new), encoding="utf-8")
        try:
            res = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "--no-header", "-p", "no:cacheprovider",
                                  f"mytests/test_{module}.py"], cwd=work, capture_output=True, text=True,
                                 timeout=TIMEOUT)
        except subprocess.TimeoutExpired:
            return False, f"тесты зависли дольше {TIMEOUT} с — считаем, что упали (но лучше без зависаний)"
        last = (res.stdout.strip().splitlines() or ["?"])[-1]
        return res.returncode == 0, last
