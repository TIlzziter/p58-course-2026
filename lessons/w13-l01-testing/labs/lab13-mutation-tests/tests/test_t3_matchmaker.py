import pytest
from grader import run_suite
from mutants import MUTANTS

M = MUTANTS["matchmaker"]


def test_suite_passes_on_correct_code():
    ok, last = run_suite("matchmaker")
    assert ok, f"ваши тесты падают на правильном коде: {last}"


@pytest.mark.parametrize("mutant", M, ids=[m[0] for m in M])
def test_mutant_killed(mutant):
    ok, last = run_suite("matchmaker", mutant)
    assert not ok, f"мутант «{mutant[0]}» выжил: тесты прошли ({last})"
