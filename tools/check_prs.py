"""Полуручная проверка pull request учеников по лабораторной (запускается на компьютере преподавателя).

Ученики работают в общей репе курса (по умолчанию ``school58-project/p58-course-labs``): каждый делает
свою ветку ``<ник>/lab01`` от ``main``, пушит её в эту же репу и открывает pull request в ``main``.

Что делает:

1. Через ``gh pr list --json`` берёт открытые PR в ветку ``--base`` (по умолчанию ``main``).
2. Оставляет только PR этой лабораторной: имя ветки кончается на ``/lab01`` (или ``-lab01``, или равно
   ``lab01``; суффикс берётся из ``--lab``, свой — ``--branch-suffix``, без фильтра — ``--all-branches``).
3. Для каждого автора оставляет только самый свежий PR по этой лабораторной (остальные — в примечаниях).
4. Клонирует репу один раз во временную папку и для каждого PR делает
   ``git fetch origin pull/N/head`` + checkout в отдельную временную папку.
5. Находит папку лабораторной ``lessons/*/labs/<лаба>`` и запускает pytest отдельно для каждой
   задачи (``tests/test_t1_*.py`` … ``test_tN_*.py``). Тесты, ``pytest.ini`` и ``check.py`` берутся
   из ветки ``--base`` репы, а не из PR — так ученик не может «починить» задачу, изменив тесты.
6. Предупреждает, если в PR есть коммиты, автор которых на GitHub — не автор PR (чужая работа,
   коммит с чужого компьютера или почта в ``git config`` не привязана к аккаунту).
7. Печатает таблицу «автор PR × задание: OK / НЕТ» и сохраняет CSV локально (не в git).

Никаких комментариев, отметок и merge скрипт не делает: преподаватель смотрит таблицу и сам
ставит отметку или пишет комментарий в PR.

ВНИМАНИЕ: код учеников выполняется на этом компьютере. Запускайте в отдельном venv
или контейнере, без секретов в окружении.

Использование:

    python tools/check_prs.py --lab lab01-git-flow                      # репа и base по умолчанию
    python tools/check_prs.py --repo school58-project/p58-course-labs --lab lab01 --out results-lab01.csv
    python tools/check_prs.py --lab lab01 --all-branches                # все открытые PR в main
    # без сети: проверить локальные папки (папку лабораторной или корень репы с уроками)
    python tools/check_prs.py --lab lab01-git-flow --local ./lab01-ivanov ./lab01-petrov
    # тесты взять из конкретной папки (иначе — из первой папки --local)
    python tools/check_prs.py --lab lab01 --local ./work --tests-from ./p58-course-labs

Нужны: Python 3.12+, pytest, ``git``; для режима с PR — ``gh`` с выполненным ``gh auth login``.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_REPO = "school58-project/p58-course-labs"
TRUSTED = ("tests", "pytest.ini", "check.py", "conftest.py")
WARNING = ("ВНИМАНИЕ: код учеников запускается на этом компьютере. Лучше запускать в отдельном venv "
           "или контейнере (docker run --rm --network none ...), без токенов и секретов в окружении.")


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 300) -> str:
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, check=False)
    if res.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd[:4])}…: {res.stderr.strip()[-500:]}")
    return res.stdout


def find_lab(root: Path, lab: str) -> Path | None:
    """Папка лабораторной: сам root, если в нём tests/, иначе lessons/*/labs/<lab>*."""
    if (root / "tests").is_dir() and root.name.startswith(lab):
        return root
    found = sorted(p for p in root.glob(f"lessons/*/labs/{lab}*") if p.is_dir())
    if not found and (root / "tests").is_dir():
        return root
    return found[0] if found else None


def tasks_of(lab: Path) -> dict[int, list[str]]:
    found: dict[int, list[str]] = {}
    for f in sorted((lab / "tests").glob("test_t*_*.py")):
        found.setdefault(int(re.match(r"test_t(\d+)_", f.name).group(1)), []).append(f"tests/{f.name}")
    return dict(sorted(found.items()))


def check_lab(student_lab: Path, trusted_lab: Path, timeout: int) -> dict[int, bool]:
    """Скопировать работу во временную папку, наложить доверенные тесты, прогнать задачи по одной."""
    with tempfile.TemporaryDirectory(prefix="p58-check-") as tmp:
        work = Path(tmp) / "lab"
        shutil.copytree(student_lab, work, ignore=shutil.ignore_patterns(".git", "__pycache__", ".venv",
                                                                          ".pytest_cache", "*.pyc"))
        for name in TRUSTED:
            src, dst = trusted_lab / name, work / name
            if dst.is_dir():
                shutil.rmtree(dst)
            elif dst.exists():
                dst.unlink()
            if src.is_dir():
                shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__"))
            elif src.exists():
                shutil.copy2(src, dst)
        env = {k: v for k, v in os.environ.items() if not re.search(r"TOKEN|SECRET|PASSWORD|KEY", k, re.IGNORECASE)}
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        result = {}
        for n, files in tasks_of(work).items():
            try:
                res = subprocess.run([sys.executable, "-m", "pytest", "-q", "--no-header", "-p", "no:cacheprovider",
                                      "--tb=no", *files], cwd=work, capture_output=True, text=True, env=env,
                                     timeout=timeout, check=False)
                result[n] = res.returncode == 0
            except subprocess.TimeoutExpired:
                result[n] = False
        return result


def list_prs(repo: str, base: str) -> list[dict]:
    out = run(["gh", "pr", "list", "--repo", repo, "--state", "open", "--base", base, "--limit", "200",
               "--json", "number,author,headRefName,baseRefName,title,url,createdAt"])
    return sorted(json.loads(out), key=lambda p: p["number"])


def lab_suffix(lab: str) -> str:
    """lab01-git-flow → lab01."""
    m = re.match(r"(lab\d+)", lab)
    return m.group(1) if m else lab


def branch_matches(branch: str, suffix: str) -> bool:
    b, s = branch.lower(), suffix.lower()
    return b == s or b.endswith("/" + s) or b.endswith("-" + s)


def select_prs(prs: list[dict], suffix: str | None) -> tuple[list[dict], list[str]]:
    """PR этой лабораторной (по имени ветки) и только самый свежий у каждого автора."""
    notes, latest = [], {}
    for pr in prs:
        who = pr["author"]["login"]
        if suffix and not branch_matches(pr["headRefName"], suffix):
            notes.append(f"{who} #{pr['number']}: ветка {pr['headRefName']} — не {suffix}, пропущен")
            continue
        old = latest.get(who.lower())
        if old:
            older, newer = sorted((old, pr), key=lambda p: (p["createdAt"], p["number"]))
            notes.append(f"{who} #{older['number']}: есть более свежий PR #{newer['number']}, проверяю только его")
            pr = newer
        latest[who.lower()] = pr
    return sorted(latest.values(), key=lambda p: p["number"]), notes


def foreign_commits(repo: str, pr: dict) -> list[str]:
    """Коммиты PR, у которых автор на GitHub не совпадает с автором PR."""
    out = run(["gh", "api", "--paginate", f"repos/{repo}/pulls/{pr['number']}/commits",
               "--jq", '.[] | [.sha[0:7], (.author.login // ""), .commit.author.name] | @tsv'])
    owner, bad = pr["author"]["login"].lower(), []
    for line in out.splitlines():
        sha, login, name = (line.split("\t") + ["", ""])[:3]
        if login.lower() != owner:
            bad.append(f"{sha} ({login or 'почта не привязана к GitHub, имя «' + name + '»'})")
    return bad


def check_repo(repo: str, lab: str, timeout: int, git_url: str | None, base_branch: str = "main",
               suffix: str | None = None) -> tuple[list[tuple[str, dict]], list[str]]:
    rows = []
    prs = list_prs(repo, base_branch)
    print(f"Открытых PR в {repo} → {base_branch}: {len(prs)}")
    prs, notes = select_prs(prs, suffix)
    print(f"К проверке ({'ветки *' + suffix if suffix else 'все ветки'}, по одному на автора): {len(prs)}")
    with tempfile.TemporaryDirectory(prefix="p58-prs-") as tmp:
        base = Path(tmp) / "base"
        run(["git", "clone", "-q", "--branch", base_branch, git_url or f"https://github.com/{repo}.git", str(base)],
            timeout=600)
        trusted = find_lab(base, lab)
        if not trusted:
            raise SystemExit(f"В ветке {base_branch} репы {repo} нет лабораторной {lab}")
        for pr in prs:
            who = f"{pr['author']['login']} #{pr['number']}"
            pr_dir = Path(tmp) / f"pr-{pr['number']}"
            try:
                run(["git", "fetch", "-q", "origin", f"pull/{pr['number']}/head:pr-{pr['number']}"], cwd=base)
                run(["git", "worktree", "add", "-q", "--detach", str(pr_dir), f"pr-{pr['number']}"], cwd=base)
            except RuntimeError as e:
                notes.append(f"{who}: не удалось получить PR ({e})")
                continue
            student = find_lab(pr_dir, lab)
            if not student:
                notes.append(f"{who}: в PR нет папки лабораторной {lab}")
                rows.append((who, {}))
                continue
            try:
                bad = foreign_commits(repo, pr)
            except RuntimeError as e:
                bad = []
                notes.append(f"{who}: не удалось получить список коммитов ({e})")
            if bad:
                notes.append(f"{who}: ВНИМАНИЕ, коммиты не автора PR: {', '.join(bad)}")
            print(f"  проверяю {who} ({pr['headRefName']}) «{pr['title'][:60]}» …")
            rows.append((who, check_lab(student, trusted, timeout)))
        return rows, notes


def check_local(dirs: list[Path], lab: str, timeout: int, tests_from: Path | None):
    rows, notes = [], []
    trusted = find_lab(tests_from, lab) if tests_from else None
    if tests_from and not trusted:
        raise SystemExit(f"В {tests_from} нет лабораторной {lab}")
    for d in dirs:
        student = find_lab(d.resolve(), lab)
        if not student:
            notes.append(f"{d}: нет папки лабораторной {lab}")
            rows.append((d.name, {}))
            continue
        trusted = trusted or student
        rows.append((d.name, check_lab(student, trusted, timeout)))
    if not tests_from:
        notes.append("тесты взяты из первой папки --local (для доверенных тестов укажите --tests-from)")
    return rows, notes


def print_table(rows: list[tuple[str, dict]]) -> list[int]:
    nums = sorted({n for _, r in rows for n in r})
    w = max([len("автор PR")] + [len(who) for who, _ in rows])
    print()
    print(f"{'автор PR':<{w}}  " + "  ".join(f"t{n:<3}" for n in nums) + "  итого")
    for who, r in rows:
        cells = "  ".join(f"{('OK' if r.get(n) else 'НЕТ'):<4}" for n in nums)
        print(f"{who:<{w}}  {cells}  {sum(r.values())}/{len(nums)}")
    return nums


def write_csv(path: Path, rows, nums, lab: str) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["автор", "лаба", *[f"t{n}" for n in nums], "итого"])
        for who, r in rows:
            wr.writerow([who, lab, *[("OK" if r.get(n) else "НЕТ") for n in nums], f"{sum(r.values())}/{len(nums)}"])
    print(f"\nCSV: {path} (локальный файл, в git не добавлять)")


def main() -> int:
    ap = argparse.ArgumentParser(description="Проверка PR учеников по лабораторной: таблица OK/НЕТ и CSV.")
    ap.add_argument("--repo", default=None, help=f"OWNER/NAME открытой репы (например {DEFAULT_REPO})")
    ap.add_argument("--lab", required=True, help="лабораторная: lab01-git-flow или просто lab01")
    ap.add_argument("--out", type=Path, help="CSV с результатами (по умолчанию results-<лаба>-<дата>.csv)")
    ap.add_argument("--local", type=Path, nargs="+", metavar="DIR",
                    help="проверить локальные папки вместо PR (без сети)")
    ap.add_argument("--tests-from", type=Path, metavar="DIR", help="откуда брать доверенные тесты в режиме --local")
    ap.add_argument("--base", default="main", help="ветка, в которую открыты PR и откуда берутся тесты (main)")
    ap.add_argument("--branch-suffix", help="суффикс имени ветки ученика (по умолчанию из --lab: lab01)")
    ap.add_argument("--all-branches", action="store_true", help="не фильтровать PR по имени ветки")
    ap.add_argument("--git-url", help="адрес для git clone вместо https://github.com/<repo>.git (зеркало, тесты)")
    ap.add_argument("--timeout", type=int, default=60, help="лимит времени на одну задачу, секунд (по умолчанию 60)")
    args = ap.parse_args()

    print(WARNING, file=sys.stderr)
    if args.local:
        rows, notes = check_local(args.local, args.lab, args.timeout, args.tests_from)
    else:
        if not shutil.which("gh"):
            print("Нужен gh (GitHub CLI) и gh auth login, либо режим --local.", file=sys.stderr)
            return 2
        suffix = None if args.all_branches else (args.branch_suffix or lab_suffix(args.lab))
        rows, notes = check_repo(args.repo or DEFAULT_REPO, args.lab, args.timeout, args.git_url, args.base, suffix)
    if not rows:
        print("Нечего проверять.")
        return 0
    nums = print_table(rows)
    for n in notes:
        print("  !", n)
    out = args.out or Path(f"results-{args.lab}-{dt.date.today():%Y-%m-%d}.csv")
    write_csv(out, rows, nums, args.lab)
    return 0


if __name__ == "__main__":
    sys.exit(main())
