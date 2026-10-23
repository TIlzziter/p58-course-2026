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

    def _rel(self, path: str) -> str | None:
        full = posixpath.normpath(posixpath.join(self.root, path))
        if full == self.root:
            return ""
        if full.startswith(self.root.rstrip("/") + "/"):
            return full[len(self.root.rstrip("/")) + 1:]
        return None

    def check(self, call: dict) -> tuple[bool, str]:
        tool = call.get("tool")
        if tool in ("read", "write"):
            rel = self._rel(call["path"])
            if rel is None:
                return False, "outside_root"
            if tool == "write":
                if posixpath.basename(rel) == ".env" or any(
                        (rel + "/").startswith(p) for p in PROTECTED if p.endswith("/")):
                    return False, "protected"
            return True, "ok"
        if tool == "shell":
            cmd = call["cmd"]
            if any(c in cmd for c in CHAINING):
                return False, "chaining"
            words = shlex.split(cmd)
            if not words or words[0] not in self.allow_commands:
                return False, "command"
            if words[0] == "git" and (len(words) < 2 or words[1] not in GIT_ALLOWED):
                return False, "git_subcommand"
            return True, "ok"
        if tool == "http":
            parts = urlsplit(call["url"])
            if parts.scheme != "https":
                return False, "scheme"
            host = (parts.hostname or "").lower()
            if not any(host == h or host.endswith("." + h) for h in self.allow_hosts):
                return False, "host"
            return True, "ok"
        return False, "unknown_tool"
