import pytest

from fsm import InvalidTransition, Match


def ready_match(*names, countdown=3):
    m = Match(countdown=countdown)
    for n in names:
        m.join(n)
    for n in names:
        m.set_ready(n)
    return m


def test_lobby_to_countdown_to_playing():
    m = Match(countdown=2)
    m.join("Аня")
    m.join("Боря")
    m.set_ready("Аня")
    assert m.state == "lobby"
    m.set_ready("Боря")
    assert m.state == "countdown" and m.countdown == 2
    m.tick()
    assert m.state == "countdown"
    m.tick()
    assert m.state == "playing" and m.alive == {"Аня", "Боря"}


def test_one_player_cannot_start():
    m = Match()
    m.join("Аня")
    m.set_ready("Аня")
    assert m.state == "lobby"


def test_join_rules():
    m = Match(max_players=2)
    m.join("a")
    with pytest.raises(InvalidTransition):
        m.join("a")
    m.join("b")
    with pytest.raises(InvalidTransition):
        m.join("c")
    with pytest.raises(InvalidTransition):
        m.set_ready("c")


def test_leave_during_countdown_back_to_lobby():
    m = ready_match("a", "b", "c")
    m.leave("c")
    assert m.state == "lobby" and m.players == ["a", "b"] and m.ready == {"a", "b"}


def test_no_join_while_playing():
    m = ready_match("a", "b", countdown=1)
    m.tick()
    with pytest.raises(InvalidTransition):
        m.join("c")
    with pytest.raises(InvalidTransition):
        m.set_ready("a")


def test_finish_and_winner():
    m = ready_match("a", "b", "c", countdown=1)
    m.tick()
    m.died("b")
    assert m.state == "playing"
    m.leave("a")                   # вышел во время игры = проиграл
    assert m.state == "finished" and m.winner == "c"
    with pytest.raises(InvalidTransition):
        m.leave("c")


def test_draw():
    m = ready_match("a", "b", countdown=1)
    m.tick()
    m.alive = {"a"}                  # имитируем: оба погибли в один тик → died по очереди
    m.died("a")
    assert m.state == "finished" and m.winner is None


def test_tick_in_lobby_is_noop():
    m = Match()
    m.tick()
    assert m.state == "lobby"


def test_died_not_playing():
    with pytest.raises(InvalidTransition):
        Match().died("a")
