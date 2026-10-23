from search import Stats, best_move, minimax


def test_empty_board_is_draw_and_full_tree(ttt):
    st = Stats()
    assert minimax(ttt, ttt.initial(), st) == 0
    assert st.nodes == 549946  # известное число узлов полного дерева крестиков-ноликов


def test_terminal_positions(ttt):
    assert minimax(ttt, ttt.parse("XXX/OO./...")) == 1
    assert minimax(ttt, ttt.parse("XOX/XOO/OXX")) == 0


def test_forced_results(ttt):
    assert minimax(ttt, ttt.parse("XX./OO./...")) == 1  # X ходит и выигрывает
    assert minimax(ttt, ttt.parse("X.X/.O./O..")) == 1  # X замыкает верхний ряд
    assert minimax(ttt, ttt.parse("XX./O../...")) == 1  # ходит O: блок в 2, но X строит вилку
    assert minimax(ttt, ttt.parse("X../.O./...")) == 0


def test_best_move(ttt):
    assert best_move(ttt, ttt.parse("XX./OO./...")) == 2  # выиграть, а не блокировать
    assert best_move(ttt, ttt.parse("X../OO./X..")) == 5  # блок
    assert best_move(ttt, ttt.parse("X../.O./..X")) == 1  # угол проигрывает, нужен край
    assert best_move(ttt, ttt.parse("X../.../...")) == 4  # на угол — только центр


def test_tie_takes_first(ttt):
    # всё ведёт к ничьей — берём первый ход по порядку
    assert best_move(ttt, ttt.initial()) == 0
