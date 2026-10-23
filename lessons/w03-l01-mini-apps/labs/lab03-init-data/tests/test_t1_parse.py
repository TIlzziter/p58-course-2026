import pytest
from conftest import USER
from initdata import InitDataError, parse_init_data


def test_decodes_values(good):
    f = parse_init_data(good)
    assert set(f) == {"query_id", "user", "auth_date", "hash"}
    assert '"first_name":"Аня"' in f["user"]          # %D0%90... → Аня, %22 → "
    assert f["auth_date"].isdigit()


def test_equals_inside_value():
    assert parse_init_data("a=1%3D2&b=x%26y") == {"a": "1=2", "b": "x&y"}


def test_empty_value_kept():
    assert parse_init_data("a=&b=2") == {"a": "", "b": "2"}


@pytest.mark.parametrize("raw", ["a=1&a=2", "abc", "a=1&&b"])
def test_malformed(raw):
    with pytest.raises(InitDataError) as e:
        parse_init_data(raw)
    assert e.value.code == "malformed"
