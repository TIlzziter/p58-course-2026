from loop import GameLoop


def run(loop, *frames):
    ticks = []
    for f in frames:
        loop.advance(f, ticks.append)
    return ticks


def test_fixed_step():
    loop = GameLoop(tick_ms=100)
    assert loop.advance(250, lambda i: None) == 2
    assert loop.alpha == 0.5
    assert loop.advance(50, lambda i: None) == 1
    assert loop.alpha == 0


def test_small_frames_add_up():
    loop = GameLoop(tick_ms=100)
    assert len(run(loop, *[16.0] * 25)) == 4            # 400 мс


def test_catchup_limit():
    loop = GameLoop(tick_ms=100, max_catchup=3)
    assert loop.advance(1050, lambda i: None) == 3       # вкладка была в фоне
    assert loop.dropped == 7 and loop.alpha == 0.5


def test_input_buffer():
    loop = GameLoop(tick_ms=100)
    loop.push_input("a", "up")
    loop.push_input("a", "left")            # два быстрых нажатия за один тик — оба не теряются
    loop.push_input("b", "down")
    ticks = run(loop, 100, 100, 100)
    assert ticks == [{"a": "up", "b": "down"}, {"a": "left"}, {}]


def test_buffer_limit_and_duplicates():
    loop = GameLoop(tick_ms=100, buffer=2)
    for d in ["up", "up", "left", "down"]:
        loop.push_input("a", d)
    assert run(loop, 300) == [{"a": "left"}, {"a": "down"}, {}]
