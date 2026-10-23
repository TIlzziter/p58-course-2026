from conftest import ex
from review import compose_problems


def test_agent_compose():
    assert sorted(compose_problems(ex("compose.agent.yml"))) == sorted([
        "secret_in_compose", "no_restart", "unknown_dependency", "db_port_public", "no_healthcheck"])


def test_no_duplicates():
    p = compose_problems(ex("compose.agent.yml"))
    assert len(p) == len(set(p))


def test_good_compose_clean():
    assert compose_problems(ex("compose.good.yml")) == []


def test_db_port_localhost_ok():
    text = """
services:
  db:
    image: postgres:16
    ports: ["127.0.0.1:5432:5432"]
    restart: always
    healthcheck: {test: ["CMD", "pg_isready"]}
"""
    assert compose_problems(text) == []


def test_env_list_form_and_variable():
    text = """
services:
  app:
    image: app:1
    restart: always
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - ADMIN_PASSWORD=qwerty
"""
    assert compose_problems(text) == ["secret_in_compose"]
