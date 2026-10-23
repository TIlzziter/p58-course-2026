from conftest import random_positions
from search import minimax, minimax_memo


def test_value_and_states(ttt):
    cache = {}
    assert minimax_memo(ttt, ttt.initial(), cache) == 0
    assert len(cache) == 5478  # столько разных позиций достижимо в крестиках-ноликах


def test_cache_reused(ttt):
    cache = {}
    minimax_memo(ttt, ttt.initial(), cache)
    size = len(cache)
    for s in random_positions(ttt, 20, seed=3):
        assert minimax_memo(ttt, s, cache) == minimax(ttt, s)
    assert len(cache) == size


def test_values_in_cache_are_correct(ttt):
    cache = {}
    minimax_memo(ttt, ttt.parse("X../.O./..."), cache)
    for s, v in list(cache.items())[:300]:
        assert v == minimax(ttt, s)


def test_default_cache(ttt):
    assert minimax_memo(ttt, ttt.parse("XX./OO./...")) == 1
