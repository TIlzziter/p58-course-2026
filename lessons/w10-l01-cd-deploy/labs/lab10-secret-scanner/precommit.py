"""Git-хук: не даёт закоммитить секрет. Работает, когда готова задача 6.

Установка в репозитории команды (из корня репозитория):
    cp путь/к/лабе/scanner.py путь/к/лабе/precommit.py tools/
    printf '#!/bin/sh\nexec python tools/precommit.py\n' > .git/hooks/pre-commit
    chmod +x .git/hooks/pre-commit
"""
import subprocess
import sys

from scanner import scan_diff


def main() -> int:
    diff = subprocess.run(["git", "diff", "--cached", "-U0", "--no-color"],
                          capture_output=True, text=True, check=True).stdout
    found = scan_diff(diff)
    for f in found:
        print(f"{f.path}:{f.line}: {f.rule} {f.preview}", file=sys.stderr)
    if found:
        print("\nПохоже на секрет. Уберите его в .env (он в .gitignore) или пометьте строку "
              "комментарием `secret-scan: ignore`, если это точно не секрет.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
