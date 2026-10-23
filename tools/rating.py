"""Шаблон таблицы рейтинга: rating/rating.xlsx.

Лист на каждый контест (задачи и веса берутся из contests/<id>/sheet.md),
в клетку ученика ставится «+». Лист «Рейтинг» складывает монеты формулами
и считает итоги сезонов (сезон 1 — до Нового года, сезон 2 — до конца года).
"""
from __future__ import annotations

import re
from pathlib import Path

import syllabus as S
from contest import PART_RE, TASK_RE
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parent.parent
STUDENTS = [f"Ученик {i}" for i in range(1, 9)]
HEAD = Font(bold=True)
FILL = PatternFill("solid", fgColor="EEF2F7")


def tasks_of(cid: str) -> list[tuple[str, int]]:
    found = sorted((ROOT / "contests").glob(f"{cid}-*/sheet.md"))
    if not found:
        return [(f"Задача {i}", 2) for i in range(1, 13)]
    out: list[tuple[str, int]] = []
    boss = None
    in_code = False
    for line in found[0].read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = TASK_RE.match(line)
        if m:
            boss = m.group(1) if m.group(3) else None
            if not boss:
                out.append((m.group(1) + ("*" if m.group(2) else ""), 4 if m.group(2) else 2))
            continue
        if boss and PART_RE.match(line):
            out.append((boss + line.strip()[0], 6))
    return out


def main():
    wb = Workbook()
    rating = wb.active
    rating.title = "Рейтинг"
    contest_ids = list(S.CONTESTS)
    for cid in contest_ids:
        name, topic, week, season = S.CONTESTS[cid]
        ws = wb.create_sheet(cid)
        tasks = tasks_of(cid)
        ws["A1"] = f"{name} · {topic} · неделя {week} · сезон {season}"
        ws["A1"].font = Font(bold=True, size=13)
        ws["A2"], ws["A3"] = "Задача", "Монеты за +"
        for j, (t, wgt) in enumerate(tasks, start=2):
            ws.cell(2, j, t).font = HEAD
            ws.cell(3, j, wgt)
            ws.cell(2, j).fill = ws.cell(3, j).fill = FILL
            ws.column_dimensions[get_column_letter(j)].width = 6
        last = get_column_letter(len(tasks) + 1)
        total_col = len(tasks) + 2
        ws.cell(2, total_col, "Монеты").font = HEAD
        for i, st in enumerate(STUDENTS, start=4):
            ws.cell(i, 1, st)
            ws.cell(i, total_col, f'=SUMPRODUCT(--(B{i}:{last}{i}="+"),$B$3:${last}$3)')
        ws.column_dimensions["A"].width = 16
        ws.freeze_panes = "B4"
        ws.cell(13, 1, "В клетку ученика ставится «+». Задачи прошлого контеста можно досдавать до следующего.")
    rating["A1"] = "Рейтинг сезона: сумма монет по контестам"
    rating["A1"].font = Font(bold=True, size=13)
    rating.cell(2, 1, "Ученик").font = HEAD
    s1 = [c for c in contest_ids if S.CONTESTS[c][3] == 1]
    s2 = [c for c in contest_ids if S.CONTESTS[c][3] == 2]
    cols = s1 + ["Сезон 1"] + s2 + ["Сезон 2"]
    for j, c in enumerate(cols, start=2):
        rating.cell(2, j, c).font = HEAD
        rating.cell(2, j).alignment = Alignment(horizontal="center")
    for i, st in enumerate(STUDENTS, start=3):
        rating.cell(i, 1, st)
        for j, c in enumerate(cols, start=2):
            if c in S.CONTESTS:
                ws = wb[c]
                tc = get_column_letter(len(tasks_of(c)) + 2)
                rating.cell(i, j, f"='{c}'!{tc}{i + 1}")
            else:
                season = s1 if c == "Сезон 1" else s2
                first = get_column_letter(cols.index(season[0]) + 2)
                lastc = get_column_letter(cols.index(season[-1]) + 2)
                rating.cell(i, j, f"=SUM({first}{i}:{lastc}{i})").font = HEAD
                rating.cell(i, j).fill = FILL
                rank_col = get_column_letter(j)
                rating.cell(12 if c == "Сезон 1" else 13, 1)
    rating.cell(12, 1, "Место в сезоне 1:").font = HEAD
    rating.cell(13, 1, "Место в сезоне 2:").font = HEAD
    c1 = get_column_letter(cols.index("Сезон 1") + 2)
    c2 = get_column_letter(cols.index("Сезон 2") + 2)
    for k, st in enumerate(STUDENTS):
        r = k + 3
        rating.cell(12, k + 2, f"=RANK({c1}{r},${c1}$3:${c1}$10)")
        rating.cell(13, k + 2, f"=RANK({c2}{r},${c2}$3:${c2}$10)")
    rating.cell(11, 1, "Столбцы ниже — ученики по порядку (Ученик 1 … Ученик 8)")
    for k in range(8):
        rating.cell(11, k + 2, k + 1)
    rating.column_dimensions["A"].width = 22
    rating.cell(15, 1, "Сезон 1 — контесты до Нового года, сезон 2 — после. В конце сезона рейтинг обнуляется, топ-3 получают приз.")
    out = ROOT / "rating" / "rating.xlsx"
    out.parent.mkdir(exist_ok=True)
    wb.save(out)
    # CSV-версия листа «Рейтинг» для тех, кто ведёт таблицу в Google Sheets вручную
    csv = ["Ученик," + ",".join(cols)] + [st + "," * len(cols) for st in STUDENTS]
    (ROOT / "rating" / "rating.csv").write_text("\n".join(csv) + "\n", encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
