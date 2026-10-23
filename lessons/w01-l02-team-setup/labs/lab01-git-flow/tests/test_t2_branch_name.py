import pytest
from gitflow import branch_name


def test_feature_default():
    assert branch_name(12, "Кнопка «Играть»") == "feature/12-knopka-igrat"


def test_fix():
    assert branch_name(31, "Бот падает на /start", "fix") == "fix/31-bot-padaet-na-start"


def test_unknown_kind():
    with pytest.raises(ValueError):
        branch_name(1, "что-то", "hotfix")
