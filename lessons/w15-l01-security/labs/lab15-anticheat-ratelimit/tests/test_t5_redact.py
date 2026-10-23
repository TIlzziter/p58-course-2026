from redact import redact, redact_record

TOKEN = "7123456789:" + "AAHf3kW9zQ_x-1234567890abcdefghijkl"  # выдуманный; склеен, чтобы не ловили сканеры секретов


def test_bot_token():
    assert len(TOKEN.split(":")[1]) == 35
    assert redact(f"start bot {TOKEN} ok") == "start bot [BOT_TOKEN] ok"
    assert redact("score 12345678:short") == "score 12345678:short"


def test_bearer_and_keys():
    assert redact("Authorization: Bearer eyJhbGciOi.abc.def") == "Authorization: Bearer ***"
    assert redact("GET /cb?user=ann&token=s3cr3t&x=1") == "GET /cb?user=ann&token=***&x=1"
    assert redact("PASSWORD=qwerty other=1") == "PASSWORD=*** other=1"
    assert redact('{"api_key": "abc123", "room": "R1"}') == '{"api_key": "***", "room": "R1"}'


def test_email_phone():
    assert redact("от ann.lee+p58@school.ru") == "от [EMAIL]"
    assert redact("звонить +7 (912) 345-67-89 вечером") == "звонить [PHONE] вечером"
    assert redact("tel:+79123456789") == "tel:[PHONE]"
    assert redact("время +0300, счёт 1234567890") == "время +0300, счёт 1234567890"


def test_untouched():
    s = "игрок ann вошёл в комнату R1 за 120 мс"
    assert redact(s) == s


def test_record():
    rec = {"msg": f"bot {TOKEN}", "user": {"name": "ann", "Password": "x", "phones": ["+79123456789"]},
           "ms": 120, "init_data": "query_id=1&hash=ab", "tags": ("a@b.io", 5)}
    out = redact_record(rec)
    assert out == {"msg": "bot [BOT_TOKEN]", "user": {"name": "ann", "Password": "***", "phones": ["[PHONE]"]},
                   "ms": 120, "init_data": "***", "tags": ("[EMAIL]", 5)}
    assert rec["user"]["Password"] == "x"                 # исходник не тронут
