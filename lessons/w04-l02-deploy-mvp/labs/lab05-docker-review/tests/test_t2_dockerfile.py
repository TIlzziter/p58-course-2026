import pytest

from conftest import ex
from review import dockerfile_problems


def test_agent_dockerfile():
    assert dockerfile_problems(ex("Dockerfile.agent")) == [
        "no_base_tag", "root_user", "copy_before_deps", "pip_cache", "secret_in_env"]


def test_good_dockerfile_clean():
    assert dockerfile_problems(ex("Dockerfile.good")) == []


@pytest.mark.parametrize("image,bad", [
    ("python", True), ("python:latest", True), ("python:3.12-slim", False),
    ("registry.example.ru:5000/python", True), ("registry.example.ru:5000/python:3.12", False),
])
def test_base_tag(image, bad):
    text = f"FROM {image}\nUSER app\n"
    assert ("no_base_tag" in dockerfile_problems(text)) == bad


def test_user_root_explicit():
    assert "root_user" in dockerfile_problems("FROM python:3.12\nUSER app\nUSER root\n")


@pytest.mark.parametrize("line", ["ENV API_KEY=abc", "ARG DB_PASSWORD", "ENV bot_token 123"])
def test_secret_env(line):
    assert "secret_in_env" in dockerfile_problems(f"FROM python:3.12\nUSER app\n{line}\n")


def test_harmless_env():
    assert dockerfile_problems("FROM python:3.12\nENV PYTHONUNBUFFERED=1\nUSER app\n") == []
