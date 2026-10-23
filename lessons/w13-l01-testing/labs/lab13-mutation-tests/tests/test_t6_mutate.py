from mutate import mutants, score, survivors

SRC = '''def f(a, b):
    if a < b and b == 3:
        return a + 1
    return True
'''


def test_descriptions_in_order():
    assert [d for d, _ in mutants(SRC)] == [
        "2:7: and → or", "2:7: < → <=", "2:17: == → !=", "2:22: 3 → 4", "3:15: + → -", "3:19: 1 → 2",
        "4:11: True → False"]


def test_code_changed_once():
    codes = dict(mutants(SRC))
    assert codes["2:7: < → <="] == "def f(a, b):\n    if a <= b and b == 3:\n        return a + 1\n    return True"
    assert codes["4:11: True → False"].endswith("return False")
    assert all(c.count("a + 1") + c.count("a - 1") + c.count("a + 2") == 1 for c in codes.values())


def test_outer_first_and_chains():
    assert mutants("x = a - b + c") == [("1:4: + → -", "x = a - b - c"), ("1:4: - → +", "x = a + b + c")]
    assert [d for d, _ in mutants("ok = 0 <= x < 10")] == ["1:5: <= → <", "1:5: < → <=", "1:5: 0 → 1", "1:14: 10 → 11"]


def test_ignores_strings_floats_and_other_ops():
    assert mutants('s = "a" * 2.5\nprint("x")') == []
    assert [d for d, _ in mutants("y = x * 2")] == ["1:8: 2 → 3"]


def test_survivors_and_score():
    def run_tests(code):            # «тесты»: f(1, 3) должно быть 2, f(5, 3) — True
        env = {}
        exec(code, env)
        return env["f"](1, 3) == 2 and env["f"](5, 3) is True

    alive = survivors(SRC, run_tests)
    assert alive == ["2:7: < → <="]                 # нет теста на границу a == b
    assert score(SRC, run_tests) == round(1 - 1 / 7, 3)
    assert score("x = 'нечего мутировать'", run_tests) == 1.0
