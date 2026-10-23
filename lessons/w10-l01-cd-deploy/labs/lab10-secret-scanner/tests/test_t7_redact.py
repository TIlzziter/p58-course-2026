import base64
from urllib.parse import quote

from fakes import TG
from scanner import redact


def test_plain():
    assert redact(f"start with {TG} ok", [TG]) == "start with *** ok"


def test_url_encoded_and_base64():
    log = f"GET /bot{quote(TG, safe='')}/getMe\nAuthorization: Basic {base64.b64encode(TG.encode()).decode()}"
    out = redact(log, [TG])
    assert TG not in out and quote(TG, safe="") not in out
    assert "***" in out.splitlines()[0] and out.splitlines()[1].startswith("Authorization: Basic ***")


def test_several_and_overlapping():
    assert redact("pass=abcdef, long=abcdefgh", ["abcdef", "abcdefgh"]) == "pass=***, long=***"


def test_empty_secret_ignored():
    assert redact("hello", ["", "zzz"]) == "hello"
