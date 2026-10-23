from fakes import AWS, GH, TG
from scanner import scan_tree


def test_tree(tmp_path):
    (tmp_path / "api").mkdir()
    (tmp_path / "api" / "settings.py").write_text(f'TOKEN = "{TG}"\n', encoding="utf-8")
    (tmp_path / "README.md").write_text("Токен кладите в .env\n", encoding="utf-8")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text(f"url = {GH}\n", encoding="utf-8")       # служебная папка
    (tmp_path / ".venv" / "lib").mkdir(parents=True)
    (tmp_path / ".venv" / "lib" / "x.py").write_text(f"k = '{AWS}'\n", encoding="utf-8")
    (tmp_path / "logo.png").write_bytes(b"\x89PNG\0\0" + TG.encode())                   # двоичный файл
    found = scan_tree(tmp_path)
    assert [(f.path, f.line, f.rule) for f in found] == [("api/settings.py", 1, "telegram_bot_token")]


def test_secretsignore(tmp_path):
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_x.py").write_text(f"T = '{GH}'\n", encoding="utf-8")
    (tmp_path / "docs.md").write_text(f"пример: {AWS}\n", encoding="utf-8")
    (tmp_path / "main.py").write_text(f"T = '{GH}'\n", encoding="utf-8")
    (tmp_path / ".secretsignore").write_text("# тестовые данные\ntests/*\n*.md\n", encoding="utf-8")
    assert [f.path for f in scan_tree(tmp_path)] == ["main.py"]


def test_sorted_by_path(tmp_path):
    for name in ["b.py", "a.py", "c/d.py"]:
        (tmp_path / name).parent.mkdir(exist_ok=True)
        (tmp_path / name).write_text(f"x = '{GH}'\n", encoding="utf-8")
    assert [f.path for f in scan_tree(str(tmp_path))] == ["a.py", "b.py", "c/d.py"]
