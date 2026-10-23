"""Задача 6*. Свой мутатор: генерирует мутантов по AST."""
import ast
import copy

SWAP = {ast.Lt: ast.LtE, ast.LtE: ast.Lt, ast.Gt: ast.GtE, ast.GtE: ast.Gt, ast.Eq: ast.NotEq, ast.NotEq: ast.Eq,
        ast.Add: ast.Sub, ast.Sub: ast.Add, ast.And: ast.Or, ast.Or: ast.And}
SYMBOL = {ast.Lt: "<", ast.LtE: "<=", ast.Gt: ">", ast.GtE: ">=", ast.Eq: "==", ast.NotEq: "!=",
          ast.Add: "+", ast.Sub: "-", ast.And: "and", ast.Or: "or"}


def _points(tree):
    """Точки мутации в порядке (строка, столбец), при равенстве — как в ast.walk (внешние раньше)."""
    pts = []
    for order, node in enumerate(ast.walk(tree)):
        pos = (getattr(node, "lineno", 0), getattr(node, "col_offset", 0), order)
        if isinstance(node, ast.Compare):
            for i, op in enumerate(node.ops):
                if type(op) in SWAP:
                    pts.append((pos, i))
        elif isinstance(node, (ast.BinOp, ast.BoolOp)) and type(node.op) in SWAP:
            pts.append((pos, 0))
        elif isinstance(node, ast.Constant) and (isinstance(node.value, bool) or type(node.value) is int):
            pts.append((pos, 0))
    return sorted(pts)


def _apply(tree, point):
    (line, col, order), i = point
    node = list(ast.walk(tree))[order]
    if isinstance(node, ast.Compare):
        old = type(node.ops[i])
        node.ops[i] = SWAP[old]()
        return f"{line}:{col}: {SYMBOL[old]} → {SYMBOL[SWAP[old]]}"
    if isinstance(node, (ast.BinOp, ast.BoolOp)):
        old = type(node.op)
        node.op = SWAP[old]()
        return f"{line}:{col}: {SYMBOL[old]} → {SYMBOL[SWAP[old]]}"
    old = node.value
    node.value = (not old) if isinstance(old, bool) else old + 1
    return f"{line}:{col}: {old!r} → {node.value!r}"


def mutants(source: str) -> list[tuple[str, str]]:
    tree = ast.parse(source)
    out = []
    for p in _points(tree):
        t = copy.deepcopy(tree)
        desc = _apply(t, p)
        out.append((desc, ast.unparse(t)))
    return out


def survivors(source: str, run_tests) -> list[str]:
    """Описания мутантов, на которых run_tests(код) вернул True (тесты прошли — мутант выжил)."""
    return [desc for desc, code in mutants(source) if run_tests(code)]


def score(source: str, run_tests) -> float:
    """Доля убитых мутантов, 0..1. Мутантов нет — 1.0."""
    ms = mutants(source)
    if not ms:
        return 1.0
    return round(1 - len(survivors(source, run_tests)) / len(ms), 3)
