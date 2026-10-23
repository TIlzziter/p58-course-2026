"""Контест 5 · E5*: какие слои Docker-образа пересоберутся."""
import fnmatch


def rebuilt_from(dockerfile: list[str], changed: list[str], base_changed: bool = False) -> int | None:
    """Индекс первой инструкции, которая пересоберётся (дальше пересобирается всё). Все из кэша → None.

    FROM меняется, только если base_changed. COPY/ADD <src…> <dst>: пересобирается, если какой-то изменённый
    файл подходит под один из src (fnmatch; src-папка «app/» или «app» — всё внутри; «.» — всё).
    Остальные инструкции (RUN, ENV, WORKDIR, CMD…) сами по себе из кэша.
    """
    for i, line in enumerate(dockerfile):
        parts = line.split()
        if not parts:
            continue
        op = parts[0].upper()
        if op == "FROM" and base_changed:
            return i
        if op in ("COPY", "ADD"):
            srcs = [p for p in parts[1:-1] if not p.startswith("--")]
            for f in changed:
                for s in srcs:
                    s = s.rstrip("/")
                    if s == "." or fnmatch.fnmatch(f, s) or f.startswith(s + "/"):
                        return i
    return None
