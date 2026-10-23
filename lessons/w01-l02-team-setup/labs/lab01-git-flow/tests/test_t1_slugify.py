from gitflow import slugify


def test_example_from_readme():
    assert slugify("Поле 6×7: ход в столбец") == "pole-6-7-hod-v-stolbec"


def test_all_letters():
    assert slugify("Ёжик щёлкает йогурт") == "ezhik-schelkaet-yogurt"


def test_no_double_or_edge_dashes():
    assert slugify("  «Играть» — сейчас!  ") == "igrat-seychas"


def test_latin_and_digits_kept():
    assert slugify("FastAPI v2 и WebSocket") == "fastapi-v2-i-websocket"
