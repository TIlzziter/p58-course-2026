import pytest
from ci_tools import load_workflow

JOBS = "\njobs:\n  a:\n    runs-on: ubuntu-latest\n    steps: []\n"


def test_on_is_not_true():
    wf = load_workflow("on: push" + JOBS)
    assert "on" in wf and True not in wf


@pytest.mark.parametrize("on, events", [
    ("on: push", {"push": {}}),
    ("on: [push, pull_request]", {"push": {}, "pull_request": {}}),
    ("on:\n  push:\n    branches: [main]\n  pull_request:", {"push": {"branches": ["main"]}, "pull_request": {}}),
    ("on:\n  workflow_dispatch:", {"workflow_dispatch": {}}),
])
def test_events_normalized(on, events):
    assert load_workflow(on + JOBS)["on"] == events


def test_jobs_kept():
    wf = load_workflow("name: CI\non: push" + JOBS)
    assert wf["name"] == "CI" and list(wf["jobs"]) == ["a"]


@pytest.mark.parametrize("text", ["on: push\n", "jobs:\n  a: {}\n", "- a\n- b\n"])
def test_invalid(text):
    with pytest.raises(ValueError):
        load_workflow(text)
