"""Кнопка «Скачать» и самоскачивание для HTML-раздатки курса (презентации, листы контестов).

* Кнопка — ссылка на этот же файл с атрибутом ``download``: браузер сохраняет HTML как есть
  (файлы самодостаточны: стили и скрипты встроены, поэтому открываются без интернета).
* Ссылка ``…/файл.html#download`` (или ``?download``) открывает страницу и сразу скачивает её:
  скрипт нажимает кнопку, убирает «download» из адреса, дальше страница работает как обычно.
  Так в README и таблицах делается ссылка «Скачать» на GitHub Pages (markdown не умеет атрибут download,
  а raw.githubusercontent отдаёт text/plain).
* Имя скачанного файла — «<папка>-<файл>», например ``w01-l01-kickoff-lecture.html``.
* Кнопка не видна при печати; в полноэкранном показе слайдов тоже (см. CSS сборщиков).
"""
from __future__ import annotations

import html
from pathlib import Path

# Скрипт ставится ПЕРЕД основными скриптами страницы: навигация презентаций по #slide=… не затрагивается.
SCRIPT = """<script>
(()=>{const a=document.getElementById('download');if(!a)return;
const h=new URLSearchParams(location.hash.slice(1)),q=new URLSearchParams(location.search);
if(!h.has('download')&&!q.has('download'))return;h.delete('download');q.delete('download');
const qs=q.toString(),hs=h.toString();
history.replaceState(null,'',location.pathname+(qs?'?'+qs:'')+(hs?'#'+hs:''));
a.click()})();
</script>"""

# Признак, по которому генераторы README понимают, что у файла работает ссылка «…#download».
MARKER = 'id="download"'


def download_name(dst: Path) -> str:
    return f"{dst.resolve().parent.name}-{dst.name}"


def button(dst: Path, cls: str = "control") -> str:
    """Ссылка-кнопка «Скачать» для файла dst (элемент с id="download")."""
    return (f'<a class="{cls}" id="download" href="{html.escape(dst.name)}" '
            f'download="{html.escape(download_name(dst))}" '
            'title="Скачать HTML-файл (открывается без интернета)" aria-label="Скачать файл">'
            '⤓<span class="dl-text">Скачать</span></a>')
