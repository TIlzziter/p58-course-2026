"""Сборка листа контеста: sheet.md → sheet.html → sheet.pdf (через headless Chrome).

Разметка задач в sheet.md:
  **A1.** обычная задача — 2 монеты
  **B5\\*.** задача со звёздочкой — 4 монеты
  **E4 · босс.** задача-босс; её части — строки «а) …», «б) …» — по 6 монет за часть
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

import markdown

CSS = """
@page{size:A4;margin:14mm 13mm 14mm 13mm}
body{font-family:Arial,"Helvetica Neue",Helvetica,sans-serif;font-size:10.6pt;line-height:1.42;color:#1f2328;margin:0}
h1{font-size:19pt;margin:0 0 4pt}
h2{font-size:14.5pt;margin:16pt 0 6pt;padding-bottom:3pt;border-bottom:1px solid #d0d7de;break-after:avoid}
h3{font-size:12pt;margin:12pt 0 4pt;break-after:avoid}
p{margin:5pt 0}
strong{font-weight:700}
code{font-family:Menlo,"DejaVu Sans Mono",Consolas,monospace;font-size:9.2pt;background:#f2f3f5;padding:0 3pt;border-radius:3pt}
pre{background:#f6f7f9;border-radius:5pt;padding:7pt 10pt;margin:5pt 0 9pt;font-size:9pt;line-height:1.45;break-inside:avoid;white-space:pre-wrap}
pre code{background:none;padding:0;font-size:9pt}
.codehilite{background:#f6f7f9;border-radius:5pt;break-inside:avoid}
.codehilite pre{margin:5pt 0 9pt}
table{border-collapse:collapse;margin:6pt 0 10pt;font-size:10pt}
td,th{border:1px solid #d0d7de;padding:3pt 8pt;text-align:left}
th{background:#f6f7f9}
ul,ol{margin:4pt 0 6pt 18pt;padding:0}
li{margin:2pt 0}
.legend{border:1px solid #d0d7de;border-radius:6pt;padding:6pt 10pt;margin:6pt 0 10pt;font-size:9.8pt;background:#fbfbfc}
.legend b{color:#b3261e}
.task{break-inside:avoid-page}
.meta{color:#57606a;font-size:9.6pt}
/* pygments, светлая тема */
.k,.kn,.kd,.kc,.ow{color:#cf222e}.s,.s1,.s2,.sa,.sd,.se,.si{color:#0a3069}.c,.c1,.cm{color:#6e7781;font-style:italic}
.mi,.mf,.m{color:#0550ae}.nf,.fm{color:#8250df}.nb,.bp{color:#953800}.nc{color:#953800}.nd{color:#8250df}
"""

TASK_RE = re.compile(r"^\*\*([A-ZА-Я]\d+)(\\\*|\*)?( · босс)?\.\*\*")
PART_RE = re.compile(r"^\s*[а-е]\)\s")


def coins(md: str) -> tuple[int, int, int, int]:
    """(обычных, со звёздочкой, частей босса, всего монет)."""
    plain = star = parts = 0
    in_boss = False
    in_code = False
    for line in md.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = TASK_RE.match(line)
        if m:
            in_boss = bool(m.group(3))
            if m.group(2):
                star += 1
            elif not in_boss:
                plain += 1
            continue
        if in_boss and PART_RE.match(line):
            parts += 1
    return plain, star, parts, plain * 2 + star * 4 + parts * 6


def build(sheet: Path, pdf: bool = True) -> Path:
    md = sheet.read_text(encoding="utf-8")
    plain, star, parts, total = coins(md)
    legend = (f'<div class="legend">Монеты: обычная задача — <b>2</b>, со звёздочкой (★, например B4*) — <b>4</b>, '
              f'каждая часть босса — <b>6</b>. В этом контесте: {plain} обычных, {star} со звёздочкой, '
              f'{parts} частей босса — всего <b>{total}</b> монет. Задача засчитывается, только если вы можете объяснить свой код.</div>')
    body = markdown.markdown(md, extensions=["fenced_code", "codehilite", "tables", "sane_lists"],
                             extension_configs={"codehilite": {"guess_lang": False}})
    body = body.replace("<!-- legend -->", legend, 1) if "<!-- legend -->" in body else legend + body
    title = re.search(r"^# (.+)$", md, re.M).group(1)
    html_path = sheet.with_suffix(".html")
    html_path.write_text(f'<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>{title}</title>'
                         f"<style>{CSS}</style></head><body>{body}</body></html>\n", encoding="utf-8")
    if pdf:
        chrome = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")
        out = sheet.with_suffix(".pdf")
        subprocess.run([chrome, "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={out}", html_path.resolve().as_uri()],
                       check=True, capture_output=True)
    print(f"{sheet}: {plain}×2 + {star}×4 + {parts}×6 = {total} монет")
    return html_path


if __name__ == "__main__":
    for a in sys.argv[1:]:
        build(Path(a))
