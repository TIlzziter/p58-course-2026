from conftest import ex
from review import report


def test_agent_report():
    text = report(ex("Dockerfile.agent"), ex("compose.agent.yml"), ex("nginx.conf"), ".git\n")
    lines = text.splitlines()
    assert lines[0] == "## Ревью конфигов"
    items = [ln for ln in lines if ln.startswith("- [ ]")]
    codes = [ln.split("`")[1] for ln in items]
    assert codes[:4] == ["db_port_public", "secret_in_compose", "secret_in_env", "unknown_dependency"]
    assert set(codes) == {"db_port_public", "secret_in_compose", "secret_in_env", "unknown_dependency",
                          "dockerignore_missing", "no_base_tag", "root_user", "copy_before_deps",
                          "no_healthcheck", "no_restart", "pip_cache"}
    assert items[0].startswith("- [ ] 🔴 `db_port_public` — ")
    assert lines[-1] == "Итого: 11, критичных: 4"


def test_clean_report():
    text = report(ex("Dockerfile.good"), ex("compose.good.yml"), ex("nginx.conf"), ".env\n.git\n.venv\n__pycache__\n")
    assert text == "## Ревью конфигов\n\nЗамечаний нет ✅\n"
