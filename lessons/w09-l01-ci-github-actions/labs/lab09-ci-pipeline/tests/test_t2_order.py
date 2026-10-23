import pytest
from ci_tools import job_order


def wf(**needs):
    return {"on": {"push": {}}, "jobs": {name: ({"needs": n} if n is not None else {}) for name, n in needs.items()}}


def test_no_needs_keeps_file_order():
    assert job_order(wf(b=None, a=None, c=None)) == ["b", "a", "c"]


def test_chain():
    assert job_order(wf(build="test", test="lint", lint=None)) == ["lint", "test", "build"]


def test_needs_list_and_string():
    w = wf(deploy=["build", "e2e"], e2e="build", build=None, docs=None)
    order = job_order(w)
    assert order == ["build", "e2e", "deploy", "docs"] or order == ["build", "docs", "e2e", "deploy"]
    assert order.index("build") < order.index("e2e") < order.index("deploy")


def test_ties_by_file_order():
    # оба готовы сразу после lint — берём того, кто раньше в файле
    assert job_order(wf(lint=None, unit="lint", types="lint")) == ["lint", "unit", "types"]


def test_cycle():
    with pytest.raises(ValueError):
        job_order(wf(a="b", b="a"))


def test_unknown():
    with pytest.raises(ValueError):
        job_order(wf(a="ghost"))
