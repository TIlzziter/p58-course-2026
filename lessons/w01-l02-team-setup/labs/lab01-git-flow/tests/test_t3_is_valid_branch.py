import pytest
from gitflow import is_valid_branch


@pytest.mark.parametrize("name", ["feature/12-board", "fix/3-bot-crash", "docs/7-readme", "chore/100-ruff-config"])
def test_valid(name):
    assert is_valid_branch(name)


@pytest.mark.parametrize("name", ["main", "feature/board", "Feature/12-x", "feature/12-", "feature/12--x",
                                  "feature/0-zero", "feature/12-Board", "hotfix/1-x", "feature/12-доска"])
def test_invalid(name):
    assert not is_valid_branch(name)
