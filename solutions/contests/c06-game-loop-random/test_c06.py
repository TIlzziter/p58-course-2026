import pytest
from replay import apply_delta, delta, first_desync, rle_decode, rle_encode
from sweep import time_of_impact
from tasks import (
    aabb_pairs,
    circle_pairs,
    dead_states,
    fisher_yates_trace,
    fixed_steps,
    frame_stats,
    lcg,
    lerp_angle,
    naive_shuffle_counts,
    reachable,
    run_fsm,
    segment_hits_rect,
    spatial_hash_pairs,
    weighted_pick,
)

M = {("lobby", "ready"): "countdown", ("countdown", "cancel"): "lobby", ("countdown", "go"): "playing",
     ("playing", "win"): "finished", ("playing", "pause"): "paused", ("paused", "resume"): "playing",
     ("paused", "quit"): "limbo", ("limbo", "tick"): "limbo", ("finished", "again"): "lobby",
     ("ghost", "x"): "lobby"}
B = {"hero": (0, 0, 4, 4), "wall": (4, 0, 2, 10), "coin": (3, 3, 1, 1), "enemy": (10, 10, 2, 2), "bush": (2, -3, 1, 4)}


def test_a1():
    assert fisher_yates_trace(4, [1, 2, 0]) == [3, 0, 2, 1]
    assert fisher_yates_trace(4, [3, 2, 1]) == [0, 1, 2, 3]
    assert fisher_yates_trace(1, []) == [0]
    with pytest.raises(ValueError):
        fisher_yates_trace(3, [3, 0])
    with pytest.raises(ValueError):
        fisher_yates_trace(3, [0])


def test_a2():
    w = {"common": 70, "rare": 25, "epic": 5}
    assert [weighted_pick(w, r) for r in (0, 69, 70, 94, 95, 99)] == ["common"] * 2 + ["rare"] * 2 + ["epic"] * 2
    assert weighted_pick({"none": 0, "x": 1}, 0) == "x"
    for r in (-1, 100):
        with pytest.raises(ValueError):
            weighted_pick(w, r)


def test_a3():
    assert lcg(1, 3) == [1103527590, 377401575, 662824084]
    assert [x % 6 + 1 for x in lcg(42, 5)] == [4, 3, 6, 5, 2]
    assert lcg(5, 3, a=2, c=1, m=11) == [0, 1, 3]
    assert lcg(7, 4) == lcg(7, 4)          # одинаковое зерно — одинаковая игра


def test_a4():
    assert naive_shuffle_counts(3) == {(0, 1, 2): 4, (0, 2, 1): 5, (1, 0, 2): 5, (1, 2, 0): 5, (2, 0, 1): 4,
                                       (2, 1, 0): 4}
    c4 = naive_shuffle_counts(4)
    assert sum(c4.values()) == 256 and len(c4) == 24 and max(c4.values()) != min(c4.values())


def test_b1():
    assert run_fsm(M, "lobby", ["ready", "go", "win", "go"]) == ("finished", 1)
    assert run_fsm(M, "lobby", []) == ("lobby", 0)
    assert run_fsm(M, "lobby", ["go", "ready", "cancel", "ready", "go", "pause", "quit", "resume"]) == ("limbo", 2)


def test_b2():
    assert reachable(M, "lobby") == ["countdown", "finished", "limbo", "lobby", "paused", "playing"]
    assert reachable(M, "limbo") == ["limbo"]
    assert reachable({}, "a") == ["a"]


def test_b3():
    assert dead_states(M, "lobby", {"finished"}) == ["limbo"]
    assert dead_states(M, "lobby", {"limbo"}) == []
    assert dead_states({("a", "x"): "b", ("b", "y"): "c", ("c", "z"): "b"}, "a", {"a"}) == ["b", "c"]


def test_c1():
    assert aabb_pairs(B) == [("bush", "hero"), ("coin", "hero")]           # hero и wall только касаются
    assert aabb_pairs({"a": (0, 0, 1, 1)}) == []
    assert aabb_pairs({"a": (0, 0, 5, 5), "b": (1, 1, 1, 1), "c": (2, 2, 1, 1)}) == [("a", "b"), ("a", "c")]


def test_c2():
    assert circle_pairs({"a": (0, 0, 2), "b": (3, 4, 3), "c": (10, 0, 1)}) == [("a", "b")]   # касание считается
    assert circle_pairs({"a": (0, 0, 1), "b": (0, 3, 1)}) == []
    assert circle_pairs({"x": (0, 0, 5), "y": (1, 1, 1), "z": (-1, 0, 1)}) == [("x", "y"), ("x", "z")]


def test_c3():
    assert segment_hits_rect((0, 0), (10, 4), (4, 0, 2, 2)) is True
    assert segment_hits_rect((0, 0), (10, 10), (4, 0, 2, 2)) is False
    assert segment_hits_rect((0, 5), (10, 5), (2, 0, 3, 5)) is True           # по краю
    assert segment_hits_rect((0, 0), (10, 0), (4, 1, 2, 2)) is False
    assert segment_hits_rect((0, 0), (3, 0), (4, -1, 2, 2)) is False          # не долетел
    assert segment_hits_rect((5, 0), (5, 0), (4, -1, 2, 2)) is True           # точка внутри


def test_c4():
    pairs, checks = spatial_hash_pairs(B, 4)
    assert pairs == aabb_pairs(B) and checks == 5
    many = {f"b{i}": (i * 10, 0, 2, 2) for i in range(50)}
    assert spatial_hash_pairs(many, 4) == ([], 0)


def test_d1():
    assert lerp_angle(350, 10, 0.5) == pytest.approx(0)
    assert lerp_angle(10, 350, 0.25) == pytest.approx(5)
    assert lerp_angle(0, 180, 0.5) == pytest.approx(90)
    assert lerp_angle(90, 270, 1) == pytest.approx(270)
    assert lerp_angle(720, 30, 0) == pytest.approx(0)


def test_d2():
    assert fixed_steps([0, 16, 33, 50, 100, 300], 20, 3) == [0, 1, 1, 3, 3]
    assert fixed_steps([0, 10, 20, 30, 40], 20, 5) == [0, 1, 0, 1]
    assert fixed_steps([0], 20, 3) == []


def test_d3():
    assert frame_stats([0, 16, 33, 50, 66, 116, 133, 150, 166, 183]) == (49, 50, 1)
    assert frame_stats([0, 100, 200]) == (10, 100, 0)
    with pytest.raises(ValueError):
        frame_stats([5])


def test_e4a():
    inp = [None, None, "up", "up", "up", None, "left"]
    assert rle_encode(inp) == [[None, 2], ["up", 3], [None, 1], ["left", 1]]
    assert rle_decode(rle_encode(inp)) == inp and rle_encode([]) == []
    with pytest.raises(ValueError):
        rle_decode([["up", 0]])


def test_e4b():
    a, b = {"x": 1, "y": 2, "hp": 5}, {"x": 2, "y": 2, "shield": True}
    d = delta(a, b)
    assert d == {"set": {"x": 2, "shield": True}, "del": ["hp"]}
    assert apply_delta(a, d) == b and a == {"x": 1, "y": 2, "hp": 5}
    assert delta(b, b) == {"set": {}, "del": []}


@pytest.mark.parametrize("n, bad", [(1000, 637), (1000, 0), (1000, 999), (1000, None), (1, None), (0, None)])
def test_e4c(n, bad):
    calls = []

    def check(i):
        calls.append(i)
        assert 0 <= i < n
        return bad is None or i < bad

    assert first_desync(n, check) == bad
    assert len(calls) <= max(n, 1).bit_length() + 1


def test_e5():
    assert time_of_impact((0, 0, 2, 2), (10, 0), (5, 0, 2, 2)) == pytest.approx(0.3)
    assert time_of_impact((0, 0, 2, 2), (10, 10), (5, 5, 2, 2)) == pytest.approx(0.3)
    assert time_of_impact((0, 0, 2, 2), (2, 0), (5, 0, 2, 2)) is None
    assert time_of_impact((0, 0, 2, 2), (0, 5), (1, 1, 3, 3)) == 0                 # уже пересекаются
    assert time_of_impact((0, 0, 2, 2), (-10, 0), (5, 0, 2, 2)) is None            # летит прочь
    assert time_of_impact((0, 0, 1, 1), (100, 0), (50, 0, 1, 1)) == pytest.approx(0.49)  # тонкая стена не «пролетается»
