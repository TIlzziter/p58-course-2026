import pytest
from minijwt import b64e, decode, encode, refresh
from policy import audit_policy, expand
from tasks import (
    check_password,
    clusters,
    escape_html,
    fail2ban,
    find_sql_injection,
    fixed_window,
    fog_of_war,
    gcra,
    hash_password,
    naive_equal_steps,
    render_rating,
    replay_score,
    safe_name,
    seq_check,
    sign,
    timing_attack,
    verify,
)


def test_a1():
    sig = sign("s3cret", {"user": 42, "score": 120})
    assert sig == "6f953c8dd277e649e1930eb4ef5dd8307298821a2ab92c518b30c7bb1b8f92d4"
    assert verify("s3cret", {"score": 120, "user": 42}, sig)            # порядок ключей не важен
    assert not verify("s3cret", {"user": 42, "score": 9999}, sig)
    assert not verify("other", {"user": 42, "score": 120}, sig)
    assert sign("k", {"name": "Аня"}) != sign("k", {"name": "Аня "})


def test_a2():
    h = hash_password("qwerty", bytes.fromhex("a1b2c3d4"), 1000)
    assert h == "pbkdf2_sha256$1000$a1b2c3d4$3702611b3c803fe657bd2829f1a2cd358e57e9e2015c32e48871cb322d6bdf29"
    assert check_password("qwerty", h) and not check_password("qwertY", h)
    assert hash_password("qwerty", b"\x00", 1000) != h                  # другая соль — другой хеш
    for bad in ("garbage", "md5$1$00$00", "pbkdf2_sha256$x$00$00", "pbkdf2_sha256$10$zz$00"):
        assert not check_password("qwerty", bad)


def test_a3():
    assert naive_equal_steps("hunter2", "hunter3") == (False, 7)
    assert naive_equal_steps("abc", "abcd") == (False, 0)
    assert naive_equal_steps("pin7", "pin7") == (True, 4)
    assert naive_equal_steps("xbc", "abc") == (False, 1)
    assert naive_equal_steps("", "") == (True, 0)


@pytest.mark.parametrize("secret", ["k3y9", "zzzz", "0000", "a", "q7w8e9"])
def test_a4(secret):
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
    calls = []

    def oracle(g):
        calls.append(g)
        assert len(g) == len(secret)
        return naive_equal_steps(secret, g)

    assert timing_attack(oracle, alphabet, len(secret)) == secret
    assert len(calls) <= len(alphabet) * len(secret)


def test_b1():
    assert safe_name("  Аня  Ли ") == "Аня Ли"
    assert safe_name("Боря_2010") == "Боря_2010"
    assert safe_name("Zoe\u0308") == "Zoë"                               # NFC: две кодовые точки → одна
    assert len(safe_name("Zoe\u0308")) == 3
    for bad in ("x", "  a ", "Ann<script>", "ADMIN", "Bot", "a" * 17, "tab\there", "emoji🙂", "zero\u200bwidth"):
        with pytest.raises(ValueError):
            safe_name(bad)


def test_b2():
    assert render_rating([("bob", 50), ("<img src=x>", 120), ("ann", 50)]) == (
        "<ol>\n<li><b>&lt;img src=x&gt;</b> — 120</li>\n<li><b>ann</b> — 50</li>\n<li><b>bob</b> — 50</li>\n</ol>")
    assert escape_html("a&b \"c\" 'd' &lt;") == "a&amp;b &quot;c&quot; &#x27;d&#x27; &amp;lt;"
    assert render_rating([]) == "<ol>\n</ol>"


def test_b3():
    code = '''rows = db.execute(f"SELECT * FROM players WHERE name = '{name}'")
db.execute(text("SELECT * FROM players WHERE id = :id"), {"id": pid})
db.execute("DELETE FROM matches WHERE id = " + mid)
q = text("SELECT %s" % col)
db.execute(text("SELECT 1"))
cur.execute("SELECT * FROM t WHERE a = %s", (a,))
cur.execute('UPDATE t SET x = {}'.format(x))
'''
    assert find_sql_injection(code) == [1, 3, 4, 7]
    assert find_sql_injection("") == []


def test_c1():
    assert fixed_window([0, 10, 50, 59, 60, 61, 62, 119, 125], 3, 60) == [
        True, True, True, False, True, True, True, False, True]
    assert fixed_window([], 1, 10) == []


def test_c2():
    assert gcra([0, 0, 0, 0, 100, 250, 250, 1000], 100, 3) == [True, True, True, False, True, True, False, True]
    assert gcra([0, 50, 100, 150], 100, 1) == [True, False, True, False]


def test_c3():
    f = [(0, "1.1.1.1"), (5, "1.1.1.1"), (7, "2.2.2.2"), (9, "1.1.1.1"), (20, "1.1.1.1"), (40, "1.1.1.1"),
         (80, "1.1.1.1"), (85, "1.1.1.1"), (88, "1.1.1.1")]
    assert fail2ban(f, 3, 10, 60) == [("1.1.1.1", 9, 69), ("1.1.1.1", 88, 148)]
    assert fail2ban([(0, "a"), (10, "a"), (20, "a")], 3, 20, 5) == []    # 0 уже вне (0, 20]
    assert fail2ban([(9, "a"), (0, "a"), (5, "a")], 3, 10, 5) == [("a", 9, 14)]


def test_c4():
    logins = [("ann", "ip1", "phoneA"), ("bob", "ip2", "phoneA"), ("cat", "ip2", "pc1"), ("dan", "ip3", "pc2"),
              ("eve", "ip4", "pc3"), ("fay", "ip4", "pc4")]
    assert clusters(logins) == [["ann", "bob", "cat"], ["eve", "fay"]]
    assert clusters([("a", "x", "y"), ("a", "z", "w")]) == []
    assert clusters([("u", "same", "d1"), ("v", "x", "same")]) == []      # ip и устройство — разные вещи


def test_d1():
    ev = ["eat", "tick", "eat", "tick", "tick", "gold", "tick", "tick", "tick", "eat", "die", "gold"]
    assert replay_score(ev, 250) == (190, False)
    assert replay_score(ev, 190) == (190, True)
    assert replay_score(["eat", "eat", "eat", "eat"], 0) == (10 + 20 + 30 + 30, False)
    assert replay_score([], 0) == (0, True)
    with pytest.raises(ValueError):
        replay_score(["eat", "teleport"], 0)


def test_d2():
    m = [("ann", 1), ("ann", 2), ("bob", 1), ("ann", 2), ("ann", 5), ("ann", 3), ("bob", 2)]
    assert seq_check(m) == ["ok", "ok", "ok", "dup", "gap", "dup", "ok"]
    assert seq_check([("x", 3), ("x", 4)]) == ["gap", "ok"]


def test_d3():
    u = [("ann", 0, 0), ("bob", 2, 1), ("bob", 5, 5), ("cat", 9, 9), ("ann", 8, 8)]
    assert fog_of_war(u, "ann", 2) == [("ann", 0, 0), ("bob", 2, 1), ("cat", 9, 9), ("ann", 8, 8)]
    assert fog_of_war(u, "bob", 3) == [("ann", 0, 0), ("bob", 2, 1), ("bob", 5, 5), ("ann", 8, 8)]
    assert fog_of_war(u, "zed", 100) == []


T = ("eyJhbGciOiJIUzI1NiIsImtpZCI6ImsxIiwidHlwIjoiSldUIn0.eyJleHAiOjE2MDAsImlhdCI6MTAwMCwic3ViIjo0Mn0."
     "vjgFsc7SBxsA7sciCKmX3excOGUsbko006pJIQBlrhk")
KEYS = {"k1": "key-one"}


def test_e4a():
    assert encode({"sub": 42, "iat": 1000, "exp": 1600}, "key-one", "k1") == T
    assert "=" not in encode({"x": "?" * 7}, "k")


def test_e4b():
    assert decode(T, KEYS, 1200) == {"exp": 1600, "iat": 1000, "sub": 42}
    assert decode(T, KEYS, 1600) == {"exp": 1600, "iat": 1000, "sub": 42}
    assert decode(T, KEYS, 1650, leeway=60)["sub"] == 42
    h, p, s = T.split(".")
    forged = encode({"sub": 1, "iat": 1000, "exp": 1600}, "guess", "k1").split(".")[1]
    cases = {
        "expired": (T, KEYS, 1601), "kid": (T, {"k2": "x"}, 1200), "signature": (T, {"k1": "wrong"}, 1200),
        "format": ("abc", KEYS, 0), "alg": (b64e(b'{"alg":"none","kid":"k1"}') + "." + p + ".", KEYS, 1200),
    }
    for reason, args in cases.items():
        with pytest.raises(ValueError, match=reason):
            decode(*args)
    with pytest.raises(ValueError, match="signature"):
        decode(f"{h}.{forged}.{s}", KEYS, 1200)                         # подменили данные
    with pytest.raises(ValueError, match="format"):
        decode("%%%.e30.x", KEYS, 0)
    nbf = encode({"nbf": 2000}, "key-one")
    with pytest.raises(ValueError, match="not_yet"):
        decode(nbf, KEYS, 1990)
    assert decode(nbf, KEYS, 1990, leeway=10) == {"nbf": 2000}


def test_e4c():
    keys = {"k1": "key-one", "k2": "key-two"}
    r = refresh(T, keys, "k2", 1500, 600, 3600)
    assert decode(r, {"k2": "key-two"}, 1500) == {"exp": 2100, "iat": 1500, "sub": 42}
    with pytest.raises(ValueError, match="kid"):
        decode(r, KEYS, 1500)                                            # подписан новым ключом
    with pytest.raises(ValueError, match="too_old"):
        refresh(T, keys, "k2", 1500, 600, 400)
    with pytest.raises(ValueError, match="expired"):
        refresh(T, keys, "k2", 1700, 600, 3600)
    with pytest.raises(ValueError, match="iat"):
        refresh(encode({"sub": 1}, "key-one"), keys, "k2", 0, 10, 10)


def test_e5():
    assert expand("shell:git {status,diff}*") == ["shell:git status*", "shell:git diff*"]
    assert expand("{a,b}{1,2}") == ["a1", "a2", "b1", "b2"]
    rules = [("deny", "shell:git push*"), ("allow", "shell:git {status,diff,log}*"), ("allow", "shell:{pytest,ruff}*"),
             ("deny", "read:*.env"), ("allow", "read:*"), ("allow", "shell:git commit*")]
    calls = ["shell:git status", "shell:git push origin main", "shell:pytest -q", "read:src/app.py",
             "read:deploy/.env", "http:pypi.org", "shell:rm -rf /"]
    assert audit_policy(rules, calls) == ([True, False, True, True, False, False, False], [5])
    assert audit_policy([], ["x"]) == ([False], [])
    assert audit_policy([("allow", "read:*"), ("deny", "read:.env")], ["read:.env"]) == ([True], [1])
