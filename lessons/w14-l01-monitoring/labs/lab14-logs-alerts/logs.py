"""Задачи 1–2. Структурированные логи."""
import json
import logging

LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def parse_line(line: str) -> dict | None:
    """Строка лога → словарь. Не JSON-объект, нет поля ts или level не из LEVELS — None."""
    return json.loads(line)


def filter_logs(lines, level: str = "INFO", **fields) -> list[dict]:
    """Записи не ниже level (по порядку LEVELS), у которых все fields совпадают. Битые строки пропускаем."""
    out = []
    for line in lines:
        rec = parse_line(line)
        if rec["level"] >= level and all(rec.get(k) == v for k, v in fields.items()):
            out.append(rec)
    return out


class JsonFormatter(logging.Formatter):
    """Одна строка JSON без экранирования кириллицы:
    ts (UTC, ISO 8601 с миллисекундами), level, logger, msg (с подставленными аргументами),
    затем extra-поля по алфавиту, затем exc — последняя строка исключения ("ValueError: текст").
    Что не сериализуется в JSON — превратить в str."""

    def format(self, record: logging.LogRecord) -> str:
        return json.dumps({"ts": record.created, "level": record.levelname, "msg": record.msg})
