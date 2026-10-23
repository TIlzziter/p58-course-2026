"""Задачи 1–2. Структурированные логи."""
import json
import logging
import traceback
from datetime import UTC, datetime

LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def parse_line(line: str) -> dict | None:
    """Строка лога → словарь. Не JSON-объект или нет полей ts и level — None."""
    try:
        rec = json.loads(line)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(rec, dict) or "ts" not in rec or rec.get("level") not in LEVELS:
        return None
    return rec


def filter_logs(lines, level: str = "INFO", **fields) -> list[dict]:
    """Записи не ниже level, у которых все fields совпадают. Битые строки пропускаем."""
    lo = LEVELS.index(level)
    out = []
    for line in lines:
        rec = parse_line(line)
        if rec is None or LEVELS.index(rec["level"]) < lo:
            continue
        if all(rec.get(k) == v for k, v in fields.items()):
            out.append(rec)
    return out


_STD = set(vars(logging.LogRecord("x", 0, "", 0, "", None, None))) | {"message", "asctime", "taskName"}


class JsonFormatter(logging.Formatter):
    """Одна строка JSON: ts, level, logger, msg, затем extra-поля по алфавиту, затем exc."""

    def format(self, record: logging.LogRecord) -> str:
        out = {
            "ts": datetime.fromtimestamp(record.created, UTC).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        for k in sorted(set(vars(record)) - _STD):
            out[k] = getattr(record, k)
        if record.exc_info:
            etype, evalue, _ = record.exc_info
            out["exc"] = traceback.format_exception_only(etype, evalue)[-1].strip()
        return json.dumps(out, ensure_ascii=False, default=str)
