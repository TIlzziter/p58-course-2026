from initdata import data_check_string


def test_sorted_newlines_without_hash():
    f = {"user": "{}", "auth_date": "1", "hash": "abc", "query_id": "q"}
    assert data_check_string(f) == "auth_date=1\nquery_id=q\nuser={}"


def test_values_as_is():
    assert data_check_string({"b": "x=y", "a": "Аня"}) == "a=Аня\nb=x=y"
