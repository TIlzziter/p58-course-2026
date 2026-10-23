"""Задача 5: sample/.github/workflows/ci.yml доведён до требований README."""
import pytest
from ci_tools import expand_matrix, job_order, lint_workflow, load_workflow


@pytest.fixture
def wf(ci_text):
    return load_workflow(ci_text)


def runs(job):
    return " \n".join(str(s.get("run", "")) for s in job.get("steps", []))


def uses(job):
    return [s.get("uses", "") for s in job.get("steps", [])]


def test_triggers(wf):
    assert "pull_request" in wf["on"]
    assert wf["on"]["push"].get("branches") == ["main"]


def test_lint_clean(wf):
    assert lint_workflow(wf) == []


def test_three_jobs_in_order(wf):
    assert job_order(wf) == ["lint", "test", "build"]


def test_lint_job(wf):
    r = runs(wf["jobs"]["lint"])
    assert "ruff check" in r and "ruff format --check" in r
    assert "|| true" not in r, "ошибки линтера нельзя глушить"


def test_test_matrix(wf):
    versions = [c["python-version"] for c in expand_matrix(wf["jobs"]["test"])]
    assert versions == ["3.12", "3.13"]


def test_test_steps(wf):
    job = wf["jobs"]["test"]
    assert any(u.startswith("actions/checkout@") for u in uses(job))
    setup = [s for s in job["steps"] if s.get("uses", "").startswith("actions/setup-python@")]
    assert setup and setup[0]["with"]["python-version"] == "${{ matrix.python-version }}"
    assert setup[0]["with"].get("cache") == "pip"
    assert "pytest" in runs(job)


def test_build(wf):
    job = wf["jobs"]["build"]
    assert "docker build" in runs(job) or any(u.startswith("docker/build-push-action@") for u in uses(job))


def test_concurrency(wf):
    c = wf.get("concurrency") or {}
    assert c.get("cancel-in-progress") is True and "github.ref" in c.get("group", "")


def test_no_secrets_anywhere(ci_text):
    assert "secrets." not in ci_text, "в CI для PR секреты не нужны"
