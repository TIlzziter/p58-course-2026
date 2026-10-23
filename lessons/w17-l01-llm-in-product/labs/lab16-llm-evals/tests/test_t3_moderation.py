from moderation import moderate, normalize

BANNED = {"дурак", "bad", "ass"}


def test_normalize():
    assert normalize("ДУРААААК!!") == "дурак"
    assert normalize("p@$$") == "pas"
    assert normalize("B4AAAD") == "bad"
    assert normalize("Ёлка") == "елка"


def test_simple():
    assert moderate("ты дурак", BANNED) == ["дурак"]
    assert moderate("ДУРААААК!!!", BANNED) == ["дурак"]
    assert moderate("b4d move, really b@d", BANNED) == ["bad"]


def test_spaced_letters():
    assert moderate("ну ты д у р а к конечно", BANNED) == ["дурак"]
    assert moderate("b. a. d.", BANNED) == ["bad"]


def test_no_substrings():
    assert moderate("class pass assist", BANNED) == []
    assert moderate("дураками не рождаются", BANNED) == []
    assert moderate("", BANNED) == []


def test_several_sorted():
    assert moderate("ass and bad and дурак", BANNED) == ["ass", "bad", "дурак"]
