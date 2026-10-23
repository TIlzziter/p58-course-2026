from games import ConnectFour
from heuristic import WIN, choose_move, depth_limited, evaluate_c4
from search import Stats, center_first


def test_evaluate_simple(c4):
    assert evaluate_c4(c4, c4.initial()) == 0
    # одна фишка X в центре: окна по 1 фишке не стоят ничего, только центр
    assert evaluate_c4(c4, c4.parse("......./......./......./......./......./...X...")) == 3
    # две X рядом в нижнем ряду (столбцы 2, 3): окна [0..3], [1..4], [2..5] по 2 очка + центр
    assert evaluate_c4(c4, c4.parse("......./......./......./......./......./..XX...")) == 9


def test_evaluate_symmetry_and_win(c4):
    s = c4.parse("......./......./......./..O..../..XO.../.XXOO..")
    flipped = (tuple(-v for v in s[0]), -s[1])
    assert evaluate_c4(c4, flipped) == -evaluate_c4(c4, s)
    assert evaluate_c4(c4, c4.parse("......./......./......./......./OOO..../XXXX...")) == WIN


def test_evaluate_three_window(c4):
    s = c4.parse("......./......./......./......./O....../XXX...O")
    # окна нижнего ряда с X: [0..3] 3 X → 5, [1..4] 2 X → 2, [2..5] 1 X → 0; X в центре нет;
    # O: (0,1) одна в окнах, (0,6) одна — 0. Вертикаль столбца 0: окно X,O — смешанное.
    assert evaluate_c4(c4, s) == 7


def test_depth_limited_prefers_fast_win(c4):
    s = c4.parse("......./......./......./......./OOO..../XXX....")
    assert depth_limited(c4, c4.play(s, 3), 3, evaluate_c4) == 1 * (WIN + 3)
    assert depth_limited(c4, s, 0, evaluate_c4) == evaluate_c4(c4, s)


def test_choose_move_wins_and_blocks(c4):
    win = c4.parse("......./......./......./......./OOO..../XXX....")
    assert choose_move(c4, win, 2) == 3
    block = c4.parse("......./......./......./......./......./XXX..OO")
    assert block[1] == -1 and choose_move(c4, block, 2) == 3


def test_depth_limited_matches_full_search_small():
    from conftest import Budget

    g = ConnectFour(4, 4, 3)
    assert depth_limited(g, g.initial(), 16, evaluate_c4, stats=Budget()) > WIN


def test_beats_random(c4):
    import random

    rng = random.Random(5)
    for game_no in range(4):
        s, ai = c4.initial(), 1 if game_no % 2 == 0 else -1
        while c4.winner(s) is None:
            if c4.to_move(s) == ai:
                m = choose_move(c4, s, 3)
            else:
                m = rng.choice(c4.moves(s))
            s = c4.play(s, m)
        assert c4.winner(s) == ai


def test_pruning_with_depth(c4):
    st = Stats()
    depth_limited(c4, c4.initial(), 4, evaluate_c4, stats=st)  # без отсечений было бы 1 + 7 + … + 7**4
    assert st.nodes < 7**4
    assert center_first(c4, c4.initial(), [0, 6]) == [0, 6]
