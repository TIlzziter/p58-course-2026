from types import SimpleNamespace

import pytest
from tasks import (
    approx_tokens,
    diff_lines,
    extract_json,
    few_shot,
    fill_prompt,
    fuzzy_match,
    levenshtein,
    pass_at_k,
    render,
    render_filters,
    render_for,
    split_chunks,
    truncate,
    wrap,
)
from tgtext import md_to_tg, sanitize, split_message
from tree import render_tree


def test_a1():
    assert approx_tokens("Привет, мир!") == 5
    assert approx_tokens("Подсказка: ходи в центр :)") == 10
    assert approx_tokens("print(42)") == 5
    assert approx_tokens("") == 0 and approx_tokens("   \n") == 0
    assert approx_tokens("абвгд") == 2 and approx_tokens("абвг") == 1


def test_a2():
    assert truncate("Сегодня мы играем в крестики-нолики на поле пять на пять", 25) == "Сегодня мы играем в…"
    assert truncate("Ход сделан, жди соперника", 14) == "Ход сделан…"      # запятая перед «…» убрана
    assert truncate("Суперкалифрагилистик", 8) == "Суперка…"              # пробелов нет — режем слово
    assert truncate("коротко", 10) == "коротко" and truncate("ровно", 5) == "ровно"
    assert truncate("ab cd", 4) == "ab…"                                    # граница на пробеле
    for n in range(2, 30):
        assert len(truncate("Сегодня мы играем в крестики-нолики", n)) <= n
    with pytest.raises(ValueError):
        truncate("abc", 1)


def test_a3():
    assert wrap("Ведущий говорит: сверхдлиннословище не влезет", 10) == [
        "Ведущий", "говорит:", "сверхдлинн", "ословище", "не влезет"]
    assert wrap("a b c d e", 3) == ["a b", "c d", "e"]
    assert wrap("", 5) == [] and wrap("  много   пробелов  ", 20) == ["много пробелов"]
    assert all(len(line) <= 4 for line in wrap("раз два три четыре пять", 4))


def test_a4():
    t = "Игра началась. Ход белых! Белые ходят e4. Чёрные думают… Ответ: e5."
    assert split_chunks(t, 30, 1) == ["Игра началась. Ход белых!", "Ход белых! Белые ходят e4.",
                                      "Белые ходят e4. Чёрные думают…", "Чёрные думают… Ответ: e5."]
    assert split_chunks(t, 30, 0) == ["Игра началась. Ход белых!", "Белые ходят e4. Чёрные думают…", "Ответ: e5."]
    assert split_chunks("Очень длинное предложение без точки", 10, 1) == ["Очень длинное предложение без точки"]
    assert split_chunks("А. Б. В.", 100, 2) == ["А. Б. В."]
    assert split_chunks("", 10, 1) == []
    # нахлёст не влезает вместе со следующим предложением — его выбрасываем
    assert split_chunks("Раз два. Три четыре пять шесть.", 20, 1) == ["Раз два.", "Три четыре пять шесть."]


def test_b1():
    assert render("Привет, {{ user.name }}! Очки: {{score}}", {"user": {"name": "Аня"}, "score": 120}) \
        == "Привет, Аня! Очки: 120"
    assert render("{{ p.x }}:{{ p.y }}", {"p": SimpleNamespace(x=1, y=2)}) == "1:2"
    assert render("без переменных { и }", {}) == "без переменных { и }"
    with pytest.raises(KeyError) as e:
        render("{{ user.age }}", {"user": {"name": "Аня"}})
    assert e.value.args[0] == "user.age"


def test_b2():
    ctx = {"name": "bob", "score": 42, "tag": "", "bio": "<b>я</b>", "wins": 22}
    tpl = "{{ name|upper }} |{{ score|pad:5 }}| {{ tag|default:нет }} {{ bio|escape }} {{ wins|plural:победа,победы,побед }}"
    assert render_filters(tpl, ctx) == "BOB |   42| нет &lt;b&gt;я&lt;/b&gt; 22 победы"
    forms = "{{ n|plural:очко,очка,очков }}"
    assert [render_filters(forms, {"n": n}) for n in (1, 2, 5, 11, 12, 21, 104, 111, 0)] == [
        "1 очко", "2 очка", "5 очков", "11 очков", "12 очков", "21 очко", "104 очка", "111 очков", "0 очков"]
    assert render_filters("{{ city|default:Москва|upper }}", {}) == "МОСКВА"
    assert render_filters("{{ x }}", {"x": 0}) == "0"
    with pytest.raises(KeyError):
        render_filters("{{ city|upper }}", {})
    with pytest.raises(ValueError):
        render_filters("{{ x|rot13 }}", {"x": "a"})


def test_b3():
    ctx = {"top": [{"name": "Аня", "score": 300}, {"name": "Боб", "score": 250}], "n": 2}
    tpl = "Топ:\n{% for p in top %}{{ loop.index }}. {{ p.name }} — {{ p.score }}\n{% endfor %}Всего: {{ n }}"
    assert render_for(tpl, ctx) == "Топ:\n1. Аня — 300\n2. Боб — 250\nВсего: 2"
    assert render_for("{% for w in words %}{{ w|upper }}{% endfor %}", {"words": []}) == ""
    tpl2 = "{% for x in xs %}{{ x }}{{ sep|default:, }}{% endfor %}"
    assert render_for(tpl2, {"xs": [1, 2, 3]}) == "1,2,3,"
    # значения не рендерятся повторно
    assert render_for("{% for s in ss %}{{ s }}{% endfor %} {{ t }}", {"ss": ["{{ t }}"], "t": "T"}) == "{{ t }} T"
    with pytest.raises(KeyError):
        render_for("{% for x in nope %}{{ x }}{% endfor %}", {})


def test_c1():
    tpl = 'Ты — {role}. Ответь в JSON {{"hint": ...}}. Вопрос: {question}'
    assert fill_prompt(tpl, {"role": "ведущий", "lang": "ru"}) == (
        'Ты — ведущий. Ответь в JSON {"hint": ...}. Вопрос: {question}', ["question"], ["lang"])
    assert fill_prompt("{a}{a}{b}", {"a": 1, "b": 2}) == ("112", [], [])
    assert fill_prompt("{{a}}", {"a": 1}) == ("{a}", [], ["a"])


def test_c2():
    ex = [("как ходит конь", "буквой Г"), ("сколько клеток на доске", "64"),
          ("как ходит ладья", "по прямой"), ("кто ходит первым", "белые")]
    assert few_shot(ex, "как ходит ферзь", 2) == (
        "Вопрос: как ходит конь\nОтвет: буквой Г\n\nВопрос: как ходит ладья\nОтвет: по прямой\n\n"
        "Вопрос: как ходит ферзь\nОтвет:")
    assert few_shot(ex, "Сколько КЛЕТОК?", 1).startswith("Вопрос: сколько клеток на доске\nОтвет: 64")
    assert few_shot([], "x", 3) == "Вопрос: x\nОтвет:"


def test_c3():
    text = 'Вот: {"a": 1} и ещё {"b": "}{"} а тут {сломано} и {"c": {"d": [1, 2]}} конец'
    assert extract_json(text) == [{"a": 1}, {"b": "}{"}, {"c": {"d": [1, 2]}}]
    assert extract_json('{"q": "кавычка \\" и }"}') == [{"q": 'кавычка " и }'}]
    assert extract_json("{{\"x\": 1}") == [{"x": 1}]
    assert extract_json("нет") == [] and extract_json('{"open": ') == []


def test_c4():
    a = "Ты — ведущий.\nОтвечай кратко.\nНе раскрывай ответ."
    b = "Ты — ведущий викторины.\nОтвечай кратко.\nНе раскрывай ответ.\nФормат: JSON."
    assert diff_lines(a, b) == ["- Ты — ведущий.", "+ Ты — ведущий викторины.", "  Отвечай кратко.",
                                "  Не раскрывай ответ.", "+ Формат: JSON."]
    assert diff_lines("a\nb\nc", "a\nb\nc") == ["  a", "  b", "  c"]
    assert diff_lines("", "x") == ["+ x"] and diff_lines("x", "") == ["- x"]
    d = diff_lines("a\nb\nc\nd", "b\nx\nd\ne")
    assert [s for s in d if s[0] == " "] == ["  b", "  d"]
    assert [s[2:] for s in d if s[0] != "+"] == ["a", "b", "c", "d"]
    assert [s[2:] for s in d if s[0] != "-"] == ["b", "x", "d", "e"]


def test_d1():
    assert levenshtein("котик", "скотина") == 3
    assert levenshtein("", "abc") == 3 and levenshtein("ферзь", "ферз") == 1
    assert levenshtein("ход", "ход") == 0 and levenshtein("ab", "ba") == 2


def test_d2():
    assert fuzzy_match("Ёлка!", "елка")
    assert not fuzzy_match("пётр первый", "Пётр I")
    assert fuzzy_match("Пётр Первыи", "пётр первый")
    assert not fuzzy_match("Москва", "Минск")
    assert fuzzy_match("  e2 - e4 ", "e2 e4") and fuzzy_match("abc", "abd", tolerance=0.34)
    assert not fuzzy_match("abc", "abd", tolerance=0.3)


def test_d3():
    assert pass_at_k(10, 3, 1) == 0.3 and pass_at_k(10, 3, 5) == 0.9167
    assert pass_at_k(5, 0, 2) == 0.0 and pass_at_k(5, 4, 2) == 1.0 and pass_at_k(5, 5, 5) == 1.0
    for bad in [(5, 6, 1), (5, 1, 0), (5, 1, 6), (5, -1, 1)]:
        with pytest.raises(ValueError):
            pass_at_k(*bad)


def test_e4a():
    src = ("**Ход e4** — сильный. *Почему?* Смотри `a < b && c` и "
           "[правила](https://example.org/rules?a=1&b=2). my_var_name")
    assert md_to_tg(src) == (
        "<b>Ход e4</b> — сильный. <i>Почему?</i> Смотри <code>a &lt; b &amp;&amp; c</code> и "
        '<a href="https://example.org/rules?a=1&amp;b=2">правила</a>. my_var_name')
    assert md_to_tg("`**не жирный**`") == "<code>**не жирный**</code>"
    assert md_to_tg("_курсив_ и 2 * 3 * 4") == "<i>курсив</i> и 2 * 3 * 4"
    assert md_to_tg("[x](javascript:alert(1))") == "[x](javascript:alert(1))"
    assert md_to_tg("<script>") == "&lt;script&gt;"


def test_e4b():
    assert split_message("Первый абзац.\n\nВторой абзац длинный\nстрока два", 20) == [
        "Первый абзац.", "Второй абзац длинный", "строка два"]
    assert split_message("ааааааааааааа", 5) == ["ааааа", "ааааа", "ааа"]
    assert split_message("раз два три", 7) == ["раз два", "три"]
    assert split_message("коротко", 4096) == ["коротко"]
    import random
    rnd = random.Random(9)
    text = " ".join("".join(rnd.choice("абв\n") for _ in range(rnd.randint(1, 12))) for _ in range(400))
    parts = split_message(text, 50)
    assert all(0 < len(p) <= 50 for p in parts)


def test_e4c():
    src = ('<b>ok</b> <script>alert(1)</script> <a href="https://t.me/x" onclick="x">a</a> '
           '<i>не закрыт & amp &amp; <a href="https://ok.ru">ссылка</a>')
    assert sanitize(src) == (
        "<b>ok</b> &lt;script&gt;alert(1)&lt;/script&gt; &lt;a href=\"https://t.me/x\" onclick=\"x\"&gt;a&lt;/a&gt; "
        '<i>не закрыт &amp; amp &amp; <a href="https://ok.ru">ссылка</a></i>')
    assert sanitize("<b><i>x</b></i>") == "<b><i>x&lt;/b&gt;</i></b>"
    assert sanitize("<B>x</B>") == "<b>x</b>"
    assert sanitize('<a href="javascript:x">y</a>') == '&lt;a href="javascript:x"&gt;y&lt;/a&gt;'
    assert sanitize("2 < 3 > 1") == "2 &lt; 3 &gt; 1"


def test_e5():
    files = {"{{name}}/README.md.tmpl": "# {{ name }}\n", "{{name}}/app/main.py": "print('{{ not }}')",
             "{{name}}/[if:bot]/bot.py.tmpl": "TOKEN = '{{ token_env }}'", "{{name}}/[if:redis]/cache.py": "x"}
    ctx = {"name": "snake", "bot": True, "redis": False, "token_env": "BOT_TOKEN"}
    out = render_tree(files, ctx)
    assert out == {"snake/README.md": "# snake\n", "snake/app/main.py": "print('{{ not }}')",
                   "snake/bot.py": "TOKEN = 'BOT_TOKEN'"}
    assert list(out) == sorted(out)
    with pytest.raises(ValueError):
        render_tree({"[if:a]/x.py": "1", "x.py": "2"}, {"a": 1})
    with pytest.raises(KeyError):
        render_tree({"{{ who }}.txt": ""}, {})
