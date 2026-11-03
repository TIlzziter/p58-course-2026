"""Генерирует README.md урока для каждого урока и таблицу расписания в корневом README.md.

Текст урока: пометка о версии плана, цели, практика на уроке, материалы, агентная часть,
домашнее задание — из tools/syllabus.py.
Если в папке урока есть notes.md, он добавляется в README урока как «Заметки преподавателю».
Если в папке урока есть practice/<тема>/README.md, ссылка на него попадает в «Материалы».
HTML-раздатка (lecture.html, seminar.html, practice/*/*.html, листы контестов sheet.html) получает ссылки
«▶ Открыть … в браузере» (GitHub Pages, S.PAGES_URL) и «⤓ Скачать» (тот же адрес + #download: страница
скачивает сама себя, см. tools/html_download.py; ссылка ставится, только если в файле есть этот скрипт).
В таблице расписания — «слайды · скачать» у урока и «открыть · скачать» у листа контеста.
README, которые не генерируются (урок w00, README лабораторных), получают такие ссылки между маркерами
<!-- pages --> и <!-- /pages --> под заголовком — на HTML-файлы своей папки (кроме вложенных папок со своим README).
В корневом README таблица расписания заменяется между маркерами <!-- schedule --> и <!-- /schedule -->,
пометка о версии плана — между маркерами <!-- status --> и <!-- /status -->.
"""
from __future__ import annotations

import re
from pathlib import Path

import html_download
import syllabus as S

ROOT = Path(__file__).resolve().parent.parent


def contest_dir(cid: str) -> Path | None:
    found = sorted((ROOT / "contests").glob(f"{cid}-*"))
    return found[0] if found else None


DECK_NAMES = {"lecture": "лекцию", "seminar": "семинар", "sheet": "лист контеста", "index": "демо"}


def decks(d: Path) -> list[Path]:
    """HTML-слайды в папке урока (без вложенных папок): сначала лекция, потом семинар, потом остальные."""
    order = list(DECK_NAMES)
    return sorted(d.glob("*.html"), key=lambda p: (order.index(p.stem) if p.stem in order else len(order), p.name))


def pages_url(f: Path) -> str:
    return S.PAGES_URL + f.resolve().relative_to(ROOT).as_posix()


def can_download(f: Path) -> bool:
    return html_download.MARKER in f.read_text(encoding="utf-8")


def open_links(f: Path, label: str | None = None) -> str:
    """«▶ Открыть лекцию в браузере · ⤓ Скачать» для HTML-файла f."""
    label = label or DECK_NAMES.get(f.stem, f"«{f.name}»")
    s = f"**▶ [Открыть {label} в браузере]({pages_url(f)})**"
    if can_download(f):
        s += f" · [⤓ Скачать]({pages_url(f)}#download)"
    return s


def short_links(f: Path, open_text: str = "открыть") -> str:
    """Короткие ссылки для таблиц: «[слайды](…) · [скачать](…#download)»."""
    s = f"[{open_text}]({pages_url(f)})"
    if can_download(f):
        s += f" · [скачать]({pages_url(f)}#download)"
    return s


def lesson_html(d: Path) -> list[Path]:
    """HTML-раздатка урока: слайды в папке урока и HTML практики (practice/<тема>/*.html)."""
    return decks(d) + sorted(d.glob("practice/*/*.html"))


def lesson_readme(w: S.Week, l: S.Lesson) -> str:
    d = ROOT / "lessons" / l.dir
    lines = [f"# Урок {l.num:02d}. {l.title}", "",
             f"> {S.WORKING_VERSION}", "",
             f"**Неделя {w.n}** ({w.dates}) · {S.TRIMESTERS[w.tri]} · {l.kind} · 3 академических часа", "",
             f"**Дата:** {S.fmt_full(l.date)}", ""]
    for f in lesson_html(d):
        lines += [open_links(f, None if f.parent == d else f"практику «{f.relative_to(d).as_posix()}»"), ""]
    lines += ["## Цели", ""]
    lines += [f"- {g}" for g in l.goals]
    if l.practice:
        lines += ["", "## Практика на уроке", "", S.FORMAT, ""]
        lines += [f"{i}. {t}" for i, t in enumerate(l.practice, 1)]
    lines += ["", "## Материалы", ""]
    deck = d / f"{l.deck}.html"
    kind = "Лекция" if l.part == 1 else "Семинар"
    if deck.exists():
        lines.append(f"- {kind}: презентация — {short_links(deck, 'открыть в браузере')}; "
                     f"файл [`{deck.name}`]({deck.name}), исходник [`{l.deck}.deck`]({l.deck}.deck)")
    else:
        lines.append(f"- {kind}: презентация — исходник [`{l.deck}.deck`]({l.deck}.deck)")
    if (d / "handout.md").exists():
        lines.append("- [Раздаточный материал](handout.md)")
    if l.lab:
        lines.append(f"- Лабораторная: [`labs/{l.lab}`](labs/{l.lab}/README.md) — автопроверка `python check.py`; "
                     f"эталон — `solutions/labs/{l.lab}/`")
    if l.contest:
        c = contest_dir(l.contest)
        if c:
            rel = Path("../..") / c.relative_to(ROOT)
            name, topic, _, season = S.CONTESTS[l.contest]
            web = f" ({short_links(c / 'sheet.html', 'открыть в браузере')})" if (c / "sheet.html").exists() else ""
            lines.append(f"- {name} «{topic}» (сезон {season}): [лист PDF]({rel}/sheet.pdf){web}, [исходник]({rel}/sheet.md); "
                         f"решения — `solutions/contests/{c.name}/`")
    for p in sorted(d.glob("practice/*/README.md")):
        lines.append(f"- Практика: [`{p.parent.relative_to(d).as_posix()}`]({p.relative_to(d).as_posix()})")
    if l.num == 1:
        lines.append("- Повторение до курса: [урок 00 «Как работает сеть»](../w00-l00-networks/README.md)")
    lines += ["", "## Агентная разработка", ""]
    if w.n > S.STAGE0_LAST_WEEK:
        lines += [f"> {S.AGENT_AFTER_DEC}", ""]
    lines.append(l.agent or "—")
    if w.n <= S.STAGE0_LAST_WEEK and l.lab:
        lines += ["", S.STAGE0_LAB_NOTE]
    lines += ["", "## Домашнее задание", "", l.homework, ""]
    if l.due:
        start = S.LESSON_TIME.split("–")[0]
        lines += [f"**Срок:** до начала урока {l.num + 1:02d} — {S.fmt_day(l.due)}.{l.due:%Y}, {start} МСК.", ""]
    lines += [f"**Результат недели по плану:** {w.result}", ""]
    notes = d / "notes.md"
    if notes.exists():
        lines += ["## Заметки преподавателю", "", notes.read_text(encoding="utf-8").strip(), ""]
    return "\n".join(lines)


def break_rows(prev, cur) -> list[str]:
    """Строки «каникулы» для перерывов из S.BREAKS, которые попали между уроками prev и cur."""
    rows = []
    for a, b, title in S.BREAKS:
        if (prev is None or prev.date < a) and a <= cur.date:
            name, _, rest = title.partition(" (")
            rows.append(f"| — | {a:%d.%m}–{b:%d.%m} | — | **{name}** ({rest} | — | — | — |")
    return rows


def schedule_table() -> str:
    rows = [(f"Уроки по вторникам и пятницам, {S.LESSON_TIME}; первый урок — {S.fmt_day(S.FIRST_LESSON)}."
             f"{S.FIRST_LESSON:%Y}. ДЗ урока сдаётся до начала следующего урока."), "",
            "| Нед. | Дата | Урок | Тема | ДЗ до | Лабораторная | Контест |", "|---|---|---|---|---|---|---|"]
    prev = None
    for w in S.W:
        for l in w.lessons:
            rows += break_rows(prev, l)
            prev = l
            link = f"[{l.num:02d} · {l.kind}](lessons/{l.dir}/README.md)"
            ds = decks(ROOT / "lessons" / l.dir)
            if ds:
                link += " · " + short_links(ds[0], "слайды")
            lab = f"[{l.lab.split('-')[0]}](lessons/{l.dir}/labs/{l.lab}/README.md)" if l.lab else ""
            c = contest_dir(l.contest) if l.contest else None
            contest = f"[{l.contest}](contests/{c.name}/sheet.pdf)" if c else (l.contest or "")
            if c and (c / "sheet.html").exists():
                contest += " · " + short_links(c / "sheet.html")
            due = S.fmt_day(l.due) if l.due else "—"
            rows.append(f"| {w.n} | {S.fmt_day(l.date)} | {link} | {l.title} | {due} | {lab} | {contest} |")
    return "\n".join(rows)


def own_html(d: Path) -> list[Path]:
    """HTML-файлы папки d и её подпапок, кроме подпапок со своим README.md (там ссылки ставит их README)."""
    out = []
    for f in sorted(d.rglob("*.html")):
        parts = f.parent.relative_to(d).parts
        if any((d.joinpath(*parts[:i + 1]) / "README.md").exists() for i in range(len(parts))):
            continue
        out.append(f)
    return out


def update_marked_readme(readme: Path) -> None:
    """Вставить/обновить блок ссылок «Открыть/Скачать» под заголовком README, который пишут руками."""
    text = readme.read_text(encoding="utf-8")
    d = readme.parent
    body = [open_links(f, None if f.parent == d else f"«{f.relative_to(d).as_posix()}»") for f in own_html(d)]
    block = "<!-- pages -->\n" + "\n\n".join(body) + "\n<!-- /pages -->" if body else ""
    if "<!-- pages -->" in text:
        new = re.sub(r"<!-- pages -->.*?<!-- /pages -->\n*", lambda m: block + "\n\n" if block else "", text,
                     flags=re.S)
    elif block:
        head, sep, rest = text.partition("\n\n")
        new = head + sep + block + "\n\n" + rest
    else:
        return
    if new != text:
        readme.write_text(new, encoding="utf-8")


def main():
    planned = {l.dir for w in S.W for l in w.lessons}
    for readme in sorted((ROOT / "lessons").glob("**/README.md")):
        rel = readme.relative_to(ROOT / "lessons").parts
        if len(rel) == 2 and rel[0] in planned:
            continue  # README урока по плану генерируется целиком ниже
        if "solutions" in readme.parts:
            continue
        update_marked_readme(readme)
    for w in S.W:
        for l in w.lessons:
            d = ROOT / "lessons" / l.dir
            d.mkdir(parents=True, exist_ok=True)
            (d / "README.md").write_text(lesson_readme(w, l), encoding="utf-8")
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    text = re.sub(r"<!-- schedule -->.*<!-- /schedule -->",
                  lambda m: "<!-- schedule -->\n" + schedule_table() + "\n<!-- /schedule -->", text, flags=re.S)
    text = re.sub(r"<!-- status -->.*<!-- /status -->",
                  lambda m: "<!-- status -->\n> **" + S.WORKING_VERSION + "**\n<!-- /status -->", text, flags=re.S)
    readme.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
