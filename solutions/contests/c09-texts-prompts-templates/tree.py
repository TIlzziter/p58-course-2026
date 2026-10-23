"""Контест 9 · E5*: шаблон проекта → дерево файлов."""
from tasks import render


def render_tree(files: dict[str, str], ctx: dict) -> dict[str, str]:
    """Пути и *.tmpl рендерим через B1; часть пути [if:флаг] — файл только при истинном ctx[флаг]."""
    out = {}
    for path, content in files.items():
        parts, skip = [], False
        for seg in path.split("/"):
            if seg.startswith("[if:") and seg.endswith("]"):
                if not ctx.get(seg[4:-1]):
                    skip = True
                    break
                continue
            parts.append(render(seg, ctx))
        if skip:
            continue
        new = "/".join(parts)
        if new.endswith(".tmpl"):
            new = new[:-5]
            content = render(content, ctx)
        if new in out:
            raise ValueError(f"два файла с путём {new}")
        out[new] = content
    return dict(sorted(out.items()))
