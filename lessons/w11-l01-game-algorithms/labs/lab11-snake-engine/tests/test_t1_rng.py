import random
from collections import Counter

from rng import pick, shuffle


def test_permutation_and_copy():
    items = list(range(10))
    out = shuffle(items, random.Random(5))
    assert sorted(out) == items and items == list(range(10))


def test_uniform():
    rng = random.Random(2026)
    counts = Counter(tuple(shuffle("abc", rng)) for _ in range(12000))
    assert len(counts) == 6
    # честный рандом: каждая из 6 перестановок ~2000 раз; «наивный» обмен с randrange(n) даёт 1333…2667
    assert all(1800 < c < 2200 for c in counts.values()), counts


def test_uses_only_given_rng():
    assert shuffle(range(20), random.Random(7)) == shuffle(range(20), random.Random(7))


def test_small():
    assert shuffle([], random.Random(1)) == [] and shuffle([42], random.Random(1)) == [42]


def test_pick():
    cells = {(3, 1), (0, 2), (1, 0)}
    assert pick(cells, random.Random(3)) == pick(set(sorted(cells, reverse=True)), random.Random(3))
    assert pick(set(), random.Random(3)) is None
    seen = Counter(pick(cells, random.Random(s)) for s in range(3000))
    assert set(seen) == cells and min(seen.values()) > 850
