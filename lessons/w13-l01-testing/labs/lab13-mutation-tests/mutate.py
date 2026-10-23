"""Задача 6*. Свой мутатор: генерирует мутантов по AST (модуль ast)."""


def mutants(source: str) -> list[tuple[str, str]]:
    """Все мутанты кода: (описание, новый код через ast.unparse). Одна правка — один мутант.

    Что мутируем:  < ↔ <=,  > ↔ >=,  == ↔ !=,  + ↔ -,  and ↔ or,  целое n → n + 1,  True ↔ False.
    Описание: "строка:столбец: старое → новое" — позиция узла (Compare, BinOp, BoolOp, Constant).
    Порядок: по (строка, столбец); при равенстве — как в ast.walk (внешние узлы раньше);
    в цепочке сравнений a < b <= c — слева направо.
    """
    raise NotImplementedError


def survivors(source: str, run_tests) -> list[str]:
    """Описания мутантов, на которых run_tests(код) вернул True (тесты прошли — мутант выжил)."""
    raise NotImplementedError


def score(source: str, run_tests) -> float:
    """Доля убитых мутантов, round(…, 3). Мутантов нет — 1.0."""
    raise NotImplementedError
