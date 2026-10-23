#!/usr/bin/env bash
# Проверка всех лабораторных, контестов и уроков. Использует python из PATH или $PYTHON.
set -euo pipefail
cd "$(dirname "$0")/.."
exec "${PYTHON:-python3}" scripts/check_all.py "$@"
