from game.scoring import points


def test_winner_of_two():
    assert points(1, 2) == 3
