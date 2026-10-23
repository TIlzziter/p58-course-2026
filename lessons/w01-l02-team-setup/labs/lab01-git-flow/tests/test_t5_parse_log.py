from gitflow import count_by_area, parse_log

LOG = """\
a3f9c21 game: проверка победы по диагонали
7be4d02 game: поле 6×7 и ход в столбец
1c0e5aa bot: кнопка Играть
9d8e7f6 Merge pull request #4 from team/feature/4-x
0a1b2c3 game: ничья при полном поле
"""


def test_parse_first():
    commits = parse_log(LOG)
    assert len(commits) == 5
    assert commits[0] == {"hash": "a3f9c21", "area": "game", "text": "проверка победы по диагонали"}


def test_parse_no_area():
    assert parse_log(LOG)[3] == {"hash": "9d8e7f6", "area": None,
                                 "text": "Merge pull request #4 from team/feature/4-x"}


def test_count():
    assert count_by_area(LOG) == {"game": 3, "bot": 1}


def test_empty_and_garbage():
    assert parse_log("") == []
    assert count_by_area("\n\nне хеш\n") == {}
