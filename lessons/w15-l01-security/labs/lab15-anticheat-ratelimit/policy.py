"""Задача 6. Что разрешено агенту: проверяем каждый вызов инструмента до выполнения."""
import posixpath
import shlex
from urllib.parse import urlsplit

PROTECTED = (".env", ".git/", ".github/workflows/")
CHAINING = (";", "&&", "||", "|", ">", "<", "`", "$(")
GIT_ALLOWED = {"status", "diff", "log", "add", "commit"}


class ToolPolicy:
    """Политика для агента, работающего в папке root.

    check(call) -> (разрешено, причина). Причина "ok", если разрешено. Вызовы:
      {"tool": "read",  "path": p} — путь (относительный от root или абсолютный) после нормализации
          должен быть внутри root, иначе "outside_root";
      {"tool": "write", "path": p} — как read, и ещё нельзя писать в PROTECTED: файл `.env` в любой
          папке, всё внутри `.git/` и `.github/workflows/` относительно root — "protected";
      {"tool": "shell", "cmd": c} — в строке нет ничего из CHAINING ("chaining"); первое слово
          из allow_commands ("command"); для git — подкоманда из GIT_ALLOWED ("git_subcommand");
      {"tool": "http", "url": u} — только https ("scheme"), хост из allow_hosts или его поддомен ("host").
    Другой tool — "unknown_tool". Пустая команда — "command".
    """

    def __init__(self, root: str, allow_commands=("pytest", "ruff", "git", "python"), allow_hosts=("pypi.org",)):
        self.root = posixpath.normpath(root)
        self.allow_commands = set(allow_commands)
        self.allow_hosts = set(allow_hosts)

    def check(self, call: dict) -> tuple[bool, str]:
        # Наивная версия: «внутри root» проверяется по префиксу строки, команды — по списку.
        # TODO: нормализация путей (posixpath.normpath), PROTECTED, CHAINING, git, http
        tool = call.get("tool")
        if tool in ("read", "write"):
            if call["path"].startswith("/") and not call["path"].startswith(self.root):
                return False, "outside_root"
            return True, "ok"
        if tool == "shell":
            words = call["cmd"].split()
            if not words or words[0] not in self.allow_commands:
                return False, "command"
            return True, "ok"
        if tool == "http":
            return True, "ok"
        return False, "unknown_tool"
