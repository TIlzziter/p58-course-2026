from fakes import GH, TG

from scanner import Finding, mask, scan_text


def test_mask():
    assert mask("a8f5f167f44f4964") == "a8f5…64"
    assert mask("0123456789") == "0123…89"
    assert mask("short") == "***"
    assert mask("123456789") == "***"


def test_scan_text_lines_and_masks():
    text = f"# config\nDEBUG=1\nBOT_TOKEN={TG}\n\nGH={GH}\n"
    assert scan_text(text, "app/.env") == [
        Finding("app/.env", 3, "telegram_bot_token", mask(TG)),
        Finding("app/.env", 5, "github_token", mask(GH)),
    ]


def test_preview_never_contains_secret():
    for f in scan_text(f"BOT_TOKEN={TG}"):
        assert TG not in f.preview and TG[10:20] not in f.preview


def test_default_path():
    assert scan_text("password = 'hunter2hunter2'")[0].path == "<text>"
