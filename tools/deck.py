"""Сборка HTML-презентаций курса из простого текстового формата (.deck).

Формат повторяет устройство лекции «Как работает сеть» (lessons/w00-l00-networks):
слайд 1280×720, простой и технический режим, ответы в квизах, оглавление,
дополнительные слайды, которые скрываются в режиме «Основные».

Синтаксис .deck-файла — см. docs/deck-format.md.
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

ROOT = Path(__file__).resolve().parent
CSS = (ROOT / "templates" / "deck.css").read_text(encoding="utf-8")
JS = (ROOT / "templates" / "deck.js").read_text(encoding="utf-8")

EXTRA_CSS = """
/* Дополнения курса «Проект 58»: подсветка кода и пара новых блоков */
.term pre{text-align:left}
.term.code pre{font-size:19px;line-height:1.42;white-space:pre;overflow:hidden}
.term.code.small pre{font-size:16.5px}
.term .k{color:#c4b5fd}.term .kc,.term .kn,.term .kd,.term .ow{color:#c4b5fd}
.term .s,.term .s1,.term .s2,.term .sa,.term .sd,.term .si,.term .se,.term .sb{color:#86efac}
.term .c,.term .c1,.term .cm,.term .ch,.term .cs{color:#7d8ca5;font-style:italic}
.term .m,.term .mi,.term .mf,.term .mh{color:#fbbf24}
.term .nf,.term .fm{color:#67e8f9}.term .nb,.term .bp{color:#7dd3fc}.term .nc{color:#f9a8d4}
.term .nd{color:#f472b6}.term .o{color:#cbd5e1}.term .nt{color:#f9a8d4}.term .na{color:#fde68a}
.term .gp{color:#4ade80;font-weight:700}.term .go{color:#c7d5ec}
.card .cs code,.bul code,.aha code,.warn code,.tbl code,.sub code,.q code{font-family:var(--mono);font-size:.9em;color:#a5ecf8;background:rgba(34,211,238,.08);padding:1px 6px;border-radius:6px}
.cols4{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.cols4 .card{padding:16px 20px}.cols4 .card .cs{font-size:21px}
.split{display:grid;grid-template-columns:1.05fr 1fr;gap:24px;align-items:start}
.flow{flex-wrap:wrap;row-gap:10px}
.note{font-size:19px;color:var(--muted);line-height:1.4}
.tbl.small{font-size:20px}.tbl.small td{padding:8px 12px}
"""

FORMATTER = HtmlFormatter(nowrap=True)


def inline(text: str) -> str:
    """Экранирует HTML и разбирает **жирный**, `код`, {br}."""
    out = html.escape(text, quote=False)
    out = re.sub(r"`([^`]+)`", lambda m: "<code>" + m.group(1) + "</code>", out)
    out = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", out)
    out = out.replace("{br}", "<br>")
    return out


def code_block(lang: str, title: str, lines: list[str], small: bool) -> str:
    src = "\n".join(lines)
    try:
        lexer = get_lexer_by_name(lang or "text")
    except Exception:  # noqa: BLE001
        lexer = get_lexer_by_name("text")
    body = highlight(src, lexer, FORMATTER).rstrip("\n")
    head = f'<div class="thead"><span class="ttl">{inline(title)}</span></div>' if title else ""
    cls = "term code small" if small else "term code"
    return f'<div class="{cls}">{head}<pre>{body}</pre></div>'


COLOR = {"c": "n-c", "g": "n-g", "v": "n-v", "a": "n-a", "p": "n-p", "r": "n-r", "n": "n-n"}


def flow(spec: str) -> str:
    parts = re.split(r"\s+(->|<->|=>|→|⇄)\s+", spec)
    out = []
    for i, part in enumerate(parts):
        if i % 2:
            arrow = {"->": "→", "<->": "⇄", "=>": "⇒"}.get(part, part)
            out.append(f'<div class="arr">{arrow}</div>')
            continue
        cls = "node"
        m = re.match(r"^([cgvaprn]):(.*)$", part.strip())
        if m:
            cls += " " + COLOR[m.group(1)]
            part = m.group(2)
        name, _, small = part.partition(" ~ ")
        small_html = f"<small>{inline(small.strip())}</small>" if small else ""
        out.append(f'<div class="{cls}">{inline(name.strip())}{small_html}</div>')
    return '<div class="flow">' + "".join(out) + "</div>"


def render_blocks(lines: list[str]) -> str:
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if not s:
            i += 1
            continue
        if s.startswith("```"):
            m = re.match(r"```(\w*)\s*(!small)?\s*(.*)$", s)
            lang, small, title = m.group(1), bool(m.group(2)), m.group(3)
            body = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                body.append(lines[i])
                i += 1
            i += 1
            out.append(code_block(lang, title, body, small))
            continue
        if s.startswith("- "):
            items = []
            while i < len(lines) and lines[i].strip().startswith("- "):
                items.append(f"<li>{inline(lines[i].strip()[2:])}</li>")
                i += 1
            cls = "bul compact" if len(items) > 4 else "bul"
            out.append(f'<ul class="{cls}">' + "".join(items) + "</ul>")
            continue
        if s.startswith("card:"):
            cards = []
            while i < len(lines) and lines[i].strip().startswith("card:"):
                t, _, body = lines[i].strip()[5:].partition("::")
                cards.append(f'<div class="card"><div class="ct">{inline(t.strip())}</div><div class="cs">{inline(body.strip())}</div></div>')
                i += 1
            cls = {1: "stack", 2: "cols", 3: "cols3"}.get(len(cards), "cols4")
            out.append(f'<div class="{cls}">' + "".join(cards) + "</div>")
            continue
        if s.startswith("q:"):
            qs = []
            while i < len(lines) and lines[i].strip().startswith("q:"):
                q, _, a = lines[i].strip()[2:].partition("::")
                qs.append(f'<div class="q"><p>{inline(q.strip())}</p><button class="answer" aria-expanded="false"><span class="answer-label">Показать ответ</span><span class="answer-text">{inline(a.strip())}</span></button></div>')
                i += 1
            out.append('<div class="quiz">' + "".join(qs) + "</div>")
            continue
        if s.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                rows.append(cells)
                i += 1
            small = " small" if len(rows) > 6 else ""
            head = "".join(f"<th>{inline(c)}</th>" for c in rows[0])
            body = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows[1:])
            out.append(f'<table class="tbl{small}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>')
            continue
        if s.startswith("> "):
            out.append(f'<div class="aha">{inline(s[2:])}</div>')
        elif s.startswith("! "):
            out.append(f'<div class="warn">{inline(s[2:])}</div>')
        elif s.startswith("chips:"):
            chips = "".join(f'<span class="chip">{inline(c.strip())}</span>' for c in s[6:].split("|"))
            out.append(f'<div class="chips">{chips}</div>')
        elif s.startswith("flow:"):
            out.append(flow(s[5:].strip()))
        elif s.startswith("big:"):
            out.append(f'<div class="big-time">{inline(s[4:].strip())}</div>')
        elif s.startswith("sub:"):
            out.append(f'<div class="sub">{inline(s[4:].strip())}</div>')
        elif s.startswith("note:"):
            out.append(f'<div class="note">{inline(s[5:].strip())}</div>')
        elif s.startswith("html:"):
            out.append(s[5:].strip())
        else:
            out.append(f'<div class="sub">{inline(s)}</div>')
        i += 1
    return "".join(out)


def parse(text: str):
    meta: dict[str, str] = {}
    slides = []
    part = 1
    cur = None
    mode = "simple"
    lines = text.splitlines()
    in_code = False
    for line in lines:
        if line.strip().startswith("```"):
            in_code = not in_code
        if not in_code and line.startswith("@part "):
            part = int(line.split()[1])
            continue
        if not in_code and line.startswith("## "):
            head = [h.strip() for h in line[3:].split("|")]
            flags = head[2].split(",") if len(head) > 2 else []
            cur = {"title": head[0], "mins": int(head[1]) if len(head) > 1 and head[1] else 3,
                   "flags": [f.strip() for f in flags if f.strip()], "part": part,
                   "simple": [], "technical": []}
            slides.append(cur)
            mode = "simple"
            continue
        if cur is None:
            if ":" in line:
                k, _, v = line.partition(":")
                meta[k.strip()] = v.strip()
            continue
        if not in_code and line.strip() == ":: tech":
            mode = "technical"
            continue
        if not in_code and line.strip() == ":: simple":
            mode = "simple"
            continue
        cur[mode].append(line)
    return meta, slides


def build(src: Path, dst: Path) -> int:
    meta, slides = parse(src.read_text(encoding="utf-8"))
    title = meta.get("title", src.stem)
    part_names = [p.strip() for p in meta.get("parts", "Часть 1|Часть 2").split("|")]
    kicker = meta.get("kicker", "")
    full = meta.get("full", "Все слайды · 120–135 мин")
    short = meta.get("short", "Основные · 100 мин")
    sections = []
    data = []
    for n, s in enumerate(slides, 1):
        flags = s["flags"]
        opt = "opt" in flags
        kind = " ".join(f for f in ("cover", "divider", "break") if f in flags)
        cls = f"slide s{s['part']} {kind} {'optional' if opt else ''} {'active' if n == 1 else ''}"
        cls = re.sub(r"\s+", " ", cls).strip()
        pn = part_names[s["part"] - 1] if s["part"] - 1 < len(part_names) else f"Часть {s['part']}"
        k = f"{kicker} · {pn}" if kicker else pn
        meta_cls = "meta optional-label" if opt else "meta"
        opt_txt = " · дополнительно" if opt else ""
        simple = render_blocks(s["simple"])
        tech = render_blocks(s["technical"]) or simple
        sections.append(
            f'<section class="{cls}" id="slide-{n}" data-lesson="{s["part"]}" aria-label="Слайд {n}. {html.escape(s["title"])}">'
            f'<div class="titleblock"><div class="kicker">{html.escape(k)}<span class="{meta_cls}">{s["mins"]} мин{opt_txt}</span></div>'
            f'<h2>{inline(s["title"])}</h2></div>'
            f'<div class="content simple">{simple}</div><div class="content technical">{tech}</div></section>')
        data.append({"lesson": s["part"], "title": s["title"], "mins": s["mins"], "optional": opt})
    total = sum(d["mins"] for d in data)
    main_total = sum(d["mins"] for d in data if not d["optional"])
    js = JS.replace("Как работает сеть", title.replace("`", "'"))
    js = js.replace("`Лекция ${data[current].lesson}", "`${PARTS[data[current].lesson-1]}")
    js = "const PARTS=" + json.dumps(part_names, ensure_ascii=False) + ";\n" + js
    js = js.replace("const data=", "const data=")
    buttons = "".join(
        f'<button class="control" id="lesson{i + 1}">{html.escape(p)}</button>' for i, p in enumerate(part_names[:2]))
    if len(part_names) < 2:
        buttons += '<button class="control" id="lesson2" hidden>—</button>'
    help_text = (
        "<p>← / → — листать. T — простой / технический режим. A — открыть ответы. G — оглавление. "
        "F — полный экран. Esc — закрыть окно.</p>"
        f"<p>Переключение режима сохраняет текущий слайд. «Основные» пропускают дополнительные слайды. "
        f"Полный маршрут — около {total} минут, основной — около {main_total} минут, включая перерыв.</p>"
        "<p>Файл работает без интернета. Для живых демонстраций нужна сеть. Печать использует выбранный режим, "
        "раскрывает ответы и сохраняет один слайд на страницу.</p>")
    page = (
        '<!doctype html><html lang="ru"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{html.escape(title)}</title><style>{CSS}{EXTRA_CSS}</style></head>"
        '<body data-mode="simple" data-pace="105"><div id="progress"></div>'
        f'<div class="topbar"><div class="topgroup">{buttons}'
        f'<select class="control" id="pace" aria-label="Длительность занятия"><option value="105">{html.escape(full)}</option>'
        f'<option value="90">{html.escape(short)}</option></select></div>'
        '<div class="mode-group" role="group" aria-label="Уровень объяснения">'
        '<button class="control" id="modeSimple" aria-pressed="true" title="Простая модель и схемы (T)">Простой</button>'
        '<button class="control" id="modeTechnical" aria-pressed="false" title="Подробности текущего слайда (T)">Технический</button></div></div>'
        '<div class="bottom"><small id="position"></small><nav aria-label="Управление презентацией">'
        '<button class="control" id="contents" title="Оглавление (G)">Слайды</button>'
        '<button class="control" id="answers" title="Раскрыть ответы в простом режиме (A)">Ответы</button>'
        '<button class="control" id="help" aria-label="Справка">?</button>'
        '<button class="control" id="prev" aria-label="Предыдущий слайд">‹</button><span id="counter" aria-live="polite"></span>'
        '<button class="control" id="next" aria-label="Следующий слайд">›</button>'
        '<button class="control" id="fullscreen" aria-label="Полный экран" title="Полный экран (F)">⛶</button></nav></div>'
        '<div class="modal" id="tocModal" role="dialog" aria-modal="true" aria-labelledby="tocTitle"><div class="dialog"><header>'
        '<h2 id="tocTitle">Слайды</h2><button class="control close" aria-label="Закрыть оглавление">Закрыть</button></header>'
        '<div class="tocgrid" id="tocItems"></div></div></div>'
        '<div class="modal" id="helpModal" role="dialog" aria-modal="true" aria-labelledby="helpTitle"><div class="dialog"><header>'
        f'<h2 id="helpTitle">Управление</h2><button class="control close">Закрыть</button></header>{help_text}</div></div>'
        '<main id="viewport"><div id="stage">' + "".join(sections) + "</div></main>"
        "<script>\n(()=>{\n'use strict';\nconst data=" + json.dumps(data, ensure_ascii=False)
        + ",slides=[...document.querySelectorAll('.slide')];\n" + js + "})();\n</script></body></html>\n")
    dst.write_text(page, encoding="utf-8")
    return len(slides)


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        p = Path(arg)
        n = build(p, p.with_suffix(".html"))
        print(f"{p}: {n} слайдов")
