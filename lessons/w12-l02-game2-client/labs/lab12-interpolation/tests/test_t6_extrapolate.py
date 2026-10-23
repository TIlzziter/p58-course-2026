from predict import extrapolate


def test_extrapolate():
    assert extrapolate((1, 1), (10, 0), 100, 250) == (2, 1)
    assert extrapolate((1, 1), (10, -10), 1000, 250) == (3.5, -1.5)      # не дальше 250 мс
    assert extrapolate((1, 1), (10, 0), -20, 250) == (1, 1)
