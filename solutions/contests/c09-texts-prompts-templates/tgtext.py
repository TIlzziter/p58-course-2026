"""Контест 9 · E4 босс: текст ответа модели → сообщение Telegram."""
import html
import re

CODE = re.compile(r"`([^`\n]+)`")
LINK = re.compile(r"\[([^\]\n]+)\]\((https?://[^\s)\"<>]+)\)")
BOLD = re.compile(r"\*\*(?!\s)(.+?)(?<!\s)\*\*")
ITALIC_STAR = re.compile(r"(?<!\*)\*(?![\s*])([^*\n]+?)(?<!\s)\*(?!\*)")
ITALIC_UND = re.compile(r"(?<!\w)_(?!\s)([^_\n]+?)(?<!\s)_(?!\w)")


def _inline(s: str) -> str:
    s = html.escape(s, quote=False)
    s = LINK.sub(lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', s)
    s = BOLD.sub(r"<b>\1</b>", s)
    s = ITALIC_STAR.sub(r"<i>\1</i>", s)
    return ITALIC_UND.sub(r"<i>\1</i>", s)


def md_to_tg(text: str) -> str:
    """а) Markdown модели → HTML для parse_mode=HTML."""
    out, pos = [], 0
    for m in CODE.finditer(text):
        out.append(_inline(text[pos:m.start()]))
        out.append(f"<code>{html.escape(m.group(1), quote=False)}</code>")
        pos = m.end()
    out.append(_inline(text[pos:]))
    return "".join(out)


def split_message(text: str, limit: int = 4096) -> list[str]:
    """б) Разбить на сообщения не длиннее limit: по абзацам, строкам, пробелам, иначе жёстко."""
    parts = []
    while len(text) > limit:
        for sep in ("\n\n", "\n", " "):
            p = text.rfind(sep, 1, limit + len(sep))
            if p > 0:
                parts.append(text[:p])
                text = text[p + len(sep):]
                break
        else:
            parts.append(text[:limit])
            text = text[limit:]
    if text:
        parts.append(text)
    return parts


ALLOWED = {"b", "i", "u", "s", "code", "pre", "a"}
TAG = re.compile(r"<(/?)([a-zA-Z]+)([^<>]*)>")
HREF = re.compile(r'^\s+href="(https?://[^"<>\s]+)"\s*$')
ENTITY = re.compile(r"&(?!(?:amp|lt|gt|quot|#\d+);)")


def _text(s: str) -> str:
    return ENTITY.sub("&amp;", s).replace("<", "&lt;").replace(">", "&gt;")


def sanitize(markup: str) -> str:
    """в) Оставить только разрешённые теги, сбалансировать, остальное — экранировать."""
    out, stack, pos = [], [], 0
    for m in TAG.finditer(markup):
        out.append(_text(markup[pos:m.start()]))
        pos = m.end()
        closing, name, attrs = m.group(1) == "/", m.group(2).lower(), m.group(3)
        ok = False
        if name in ALLOWED:
            if closing:
                ok = not attrs.strip() and bool(stack) and stack[-1] == name
                if ok:
                    stack.pop()
                    out.append(f"</{name}>")
            elif name == "a":
                h = HREF.match(attrs)
                if h:
                    ok = True
                    stack.append(name)
                    out.append(f'<a href="{h.group(1)}">')
            elif not attrs.strip():
                ok = True
                stack.append(name)
                out.append(f"<{name}>")
        if not ok:
            out.append(_text(m.group(0)))
    out.append(_text(markup[pos:]))
    out += [f"</{t}>" for t in reversed(stack)]
    return "".join(out)
