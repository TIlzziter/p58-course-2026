from gitflow import pr_problems

GOOD = """\
## Что сделано
Кнопка «Играть» в боте.
## Как проверить
/start в тестовом боте → кнопка открывает Mini App.
## Что сгенерировал агент
Каркас хендлера; я поправил текст и добавил тест.

Closes #12
"""


def test_good():
    assert pr_problems(GOOD) == []


def test_no_agent_section():
    assert pr_problems(GOOD.replace("## Что сгенерировал агент", "## Агент")) != []


def test_no_issue_link():
    problems = pr_problems(GOOD.replace("Closes #12", "задача 12"))
    assert len(problems) == 1


def test_empty():
    assert len(pr_problems("")) == 4
