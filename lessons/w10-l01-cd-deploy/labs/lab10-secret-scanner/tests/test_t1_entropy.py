import pytest

from scanner import looks_random, shannon_entropy


@pytest.mark.parametrize("s, h", [("", 0.0), ("aaaa", 0.0), ("ab", 1.0), ("abcd", 2.0), ("aabb", 1.0),
                                  ("0123456789abcdef", 4.0)])
def test_entropy(s, h):
    assert shannon_entropy(s) == pytest.approx(h)


def test_looks_random():
    assert looks_random("a8f5f167f44f4964e6c998dee827110c")
    assert not looks_random("aaaaaaaaaaaaaaaaaaaaaaaa")      # длинная, но однообразная
    assert not looks_random("a8f5f167")                       # слишком короткая
    assert looks_random("a8f5f167", min_len=8, threshold=2.5)
    assert not looks_random("hello_world_hello_world", threshold=3.5)
