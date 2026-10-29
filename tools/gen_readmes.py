"""Генерирует README.md урока для каждого урока и таблицу расписания в корневом README.md.

Текст урока: пометка о версии плана, цели, практика на уроке, материалы, агентная часть,
домашнее задание — из tools/syllabus.py.
Если в папке урока есть notes.md, он добавляется в README урока как «Заметки преподавателю».
Если в папке урока есть practice/<тема>/README.md, ссылка на него попадает в «Материалы».
В корневом README таблица расписания заменяется между маркерами <!-- schedule --> и <!-- /schedule -->,
пометка о версии плана — между маркерами <!-- status --> и <!-- /status -->.
"""
from __future__ import annotations

import re
from pathlib import Path

import syllabus as S

ROOT = Path(__file__).resolve().parent.parent


def contest_dir(cid: str) -> Path | None:
    found = sorted((ROOT / "contests").glob(f"{cid}-*"))
    return found[0] if found else None


def lesson_readme(w: S.Week, l: S.Lesson) -> str:
    d = ROOT / "lessons" / l.dir
    lines = [f"# Урок {l.num:02d}. {l.title}", "",
             f"> {S.WORKING_VERSION}", "",
             f"**Неделя {w.n}** ({w.dates}) · {S.TRIMESTERS[w.tri]} · {l.kind} · 3 академических часа", "",
             "## Цели", ""]
    lines += [f"- {g}" for g in l.goals]
    if l.practice:
        lines += ["", "## Практика на уроке", "", S.FORMAT, ""]
        lines += [f"{i}. {t}" for i, t in enumerate(l.practice, 1)]
    lines += ["", "## Материалы", ""]
    deck = f"{l.deck}.html"
    lines.append(f"- [{'Лекция' if l.part == 1 else 'Семинар'}: презентация]({deck}) — открыть в браузере; "
                 f"исходник [`{l.deck}.deck`]({l.deck}.deck)")
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
            lines.append(f"- {name} «{topic}» (сезон {season}): [лист PDF]({rel}/sheet.pdf), [исходник]({rel}/sheet.md); "
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
    lines += [f"**Результат недели по плану:** {w.result}", ""]
    notes = d / "notes.md"
    if notes.exists():
        lines += ["## Заметки преподавателю", "", notes.read_text(encoding="utf-8").strip(), ""]
    return "\n".join(lines)


def schedule_table() -> str:
    rows = ["| Нед. | Даты | Урок | Тема | Лабораторная | Контест |", "|---|---|---|---|---|---|"]
    for w in S.W:
        if w.n == 10:
            rows.append("| — | 25.12–10.01 | — | **Зимние каникулы** (ориентировочно); по желанию — QuestHub | — | — |")
        for l in w.lessons:
            link = f"[{l.num:02d} · {l.kind}](lessons/{l.dir}/README.md)"
            lab = f"[{l.lab.split('-')[0]}](lessons/{l.dir}/labs/{l.lab}/README.md)" if l.lab else ""
            c = contest_dir(l.contest) if l.contest else None
            contest = f"[{l.contest}](contests/{c.name}/sheet.pdf)" if c else (l.contest or "")
            rows.append(f"| {w.n} | {w.dates} | {link} | {l.title} | {lab} | {contest} |")
    return "\n".join(rows)


def main():
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
