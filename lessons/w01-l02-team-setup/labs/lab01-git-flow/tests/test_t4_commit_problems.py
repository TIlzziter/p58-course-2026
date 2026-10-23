import pytest
from gitflow import commit_problems


@pytest.mark.parametrize("msg", ["bot: кнопка Играть открывает Mini App", "api: 404, если комнаты нет",
                                 "tests: ход в заполненный столбец\n\nПодробности в теле коммита."])
def test_good(msg):
    assert commit_problems(msg) == []


@pytest.mark.parametrize("msg", ["fix", "правки", "bot: Кнопка", "bot: кнопка.", "frontend: кнопка",
                                 "bot: ", "", "api: " + "x" * 80])
def test_bad(msg):
    assert commit_problems(msg) != []


def test_reports_every_problem():
    assert len(commit_problems("frontend: Кнопка.")) == 3
