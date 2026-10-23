from review import dockerignore_missing


def test_empty():
    assert dockerignore_missing("") == [".env", ".git", ".venv", "__pycache__"]


def test_variants_accepted():
    text = "# секреты\n.env\n.git/\n**/__pycache__\n/.venv\n*.pyc\n"
    assert dockerignore_missing(text) == []


def test_comment_does_not_count():
    assert dockerignore_missing("# .env\n.git\n.venv\n__pycache__\n") == [".env"]
