import pytest
from layers import rebuilt_from
from rollout import ready_ticks, rollback_plan, rolling_plan
from tasks import (
    affected,
    bump,
    canary,
    env_diff,
    interpolate,
    leaked_tokens,
    next_release,
    pipeline_time,
    redact_url,
    rollback_target,
    runners_time,
    satisfies,
    sort_versions,
    stages,
)

J = {"lint": [], "types": [], "test": ["lint"], "build": ["test", "types"], "e2e": ["build"], "docs": []}
D = {"lint": 1, "types": 2, "test": 5, "build": 3, "e2e": 4, "docs": 2}
T1 = "123456789:" + "AAH" + "x" * 32
T2 = "987654321:" + "BBQ" + "y" * 32


def test_a1():
    assert stages(J) == [["docs", "lint", "types"], ["test"], ["build"], ["e2e"]]
    assert stages({"a": ["b"], "b": ["a"]}) is None
    assert stages({"a": [], "b": ["a"], "c": ["b", "x"], "x": ["c"]}) is None
    assert stages({}) == []


def test_a2():
    assert pipeline_time(J, D) == 13
    assert pipeline_time({"a": []}, {"a": 7}) == 7
    assert pipeline_time({"a": [], "b": [], "c": ["a", "b"]}, {"a": 1, "b": 9, "c": 1}) == 10


def test_a3():
    assert affected(J, "test") == ["build", "e2e"]
    assert affected(J, "lint") == ["build", "e2e", "test"]
    assert affected(J, "e2e") == []
    assert affected(J, "types") == ["build", "e2e"]


def test_a4():
    assert runners_time(J, D, 1) == 17
    assert runners_time(J, D, 2) == 13
    assert runners_time(J, D, 10) == 13
    # одна машина, но порядок важен: «a» занимает её первой
    assert runners_time({"a": [], "b": [], "c": ["b"]}, {"a": 5, "b": 1, "c": 1}, 2) == 5
    assert runners_time({"z": [], "y": [], "x": []}, {"z": 3, "y": 3, "x": 1}, 2) == 4


def test_b1():
    assert sort_versions(["3.10", "3.9", "3.12.1", "3.12", "3.12.0", "2.7"]) == \
        ["2.7", "3.9", "3.10", "3.12", "3.12.0", "3.12.1"]


@pytest.mark.parametrize("v, spec, ok", [
    ("3.12.1", ">=3.10,<3.13", True), ("3.13.0", ">=3.10,<3.13", False), ("3.12.7", "==3.12.*", True),
    ("3.11.0", "!=3.11.*", False), ("3.12", "==3.12.0", True), ("3.9.18", ">3.9", True),
    ("3.10", ">3.9", True), ("3.9", ">3.9", False), ("3.12.0", "", True), ("3.12.0", " >= 3.12 , != 3.12.0", False),
])
def test_b2(v, spec, ok):
    assert satisfies(v, spec) is ok


def test_b2_bad():
    with pytest.raises(ValueError):
        satisfies("3.12", "~=3.12")


def test_b3():
    assert [bump("1.4.2", p) for p in ("major", "minor", "patch")] == ["2.0.0", "1.5.0", "1.4.3"]
    assert bump("0.9.9", "patch") == "0.9.10"
    with pytest.raises(ValueError):
        bump("1.0.0", "build")


def test_c1():
    assert env_diff({"A": "1", "B": "2", "C": "3"}, {"A": "1", "B": "x", "D": "4"}) == ["~ B", "- C", "+ D"]
    assert env_diff({}, {}) == []


@pytest.mark.parametrize("s, out", [
    ("postgresql://$USER@db/${USER}", "postgresql://game@db/game"),
    ("${HOST:-localhost}:${PORT}", "localhost:8000"),
    ("${EMPTY:-dflt}|${EMPTY-dflt}|${NOPE-dflt}", "dflt||dflt"),
    ("cost $$5 ${NOPE}x", "cost $5 x"),
    ("no vars", "no vars"),
    ("$$USER", "$USER"),
])
def test_c2(s, out):
    assert interpolate(s, {"USER": "game", "EMPTY": "", "PORT": "8000"}) == out


@pytest.mark.parametrize("url, out", [
    ("postgresql://game:S3cr3t@db:5432/game", "postgresql://game:***@db:5432/game"),
    ("redis://:pw@redis:6379/0", "redis://:***@redis:6379/0"),
    ("https://user@example.org/x", "https://user@example.org/x"),
    ("https://example.org/a@b", "https://example.org/a@b"),
    ("redis://redis:6379", "redis://redis:6379"),
])
def test_c3(url, out):
    assert redact_url(url) == out


def test_c4():
    commits = [
        {"sha": "a1", "files": {"bot.py": ([f'TOKEN = "{T1}"'], [])}},
        {"sha": "b2", "files": {"bot.py": (["TOKEN = os.getenv('BOT_TOKEN')"], [f'TOKEN = "{T1}"']),
                                 ".env": ([f"BOT_TOKEN={T2}"], [])}},
        {"sha": "c3", "files": {"notes.md": ([f"старый токен {T1}"], [])}},
        {"sha": "d4", "files": {"notes.md": ([], [f"старый токен {T1}"])}},
    ]
    assert leaked_tokens(commits) == [("1234…xx", "a1", False), ("9876…yy", "b2", True)]
    assert leaked_tokens([]) == []


def test_d1():
    assert next_release(["v1.2.3", "v1.10.0", "release-2", "v1.9.9", "v2.0"]) == "v1.10.1"
    assert next_release(["v1.2.3"], "minor") == "v1.3.0"
    assert next_release(["latest", "v1"]) == "v0.1.0"


def test_d2():
    assert rollback_target([("1.0", "ok"), ("1.1", "ok"), ("1.2", "failed"), ("1.1", "ok")]) == "1.0"
    assert rollback_target([("1.0", "ok")]) is None
    assert rollback_target([("1.0", "ok"), ("1.1", "ok"), ("1.2", "failed")]) == "1.0"
    assert rollback_target([("1.0", "failed")]) is None


def test_d3():
    assert canary([0, 1, 5, 9, 2], [100] * 5, 0.03, 2) == 3
    assert canary([1, 1], [10, 0], 0.5, 1) is None
    assert canary([0, 0], [0, 0], 0.0, 3) is None
    assert canary([3, 0, 0], [10, 10, 10], 0.25, 3) == 0


def test_e4a():
    assert rolling_plan(4, 1, 1) == [(2, 1), (0, 3), (0, 4)]
    assert rolling_plan(3, 0, 1) == [(2, 1), (1, 2), (0, 3)]
    assert rolling_plan(3, 1, 0) == [(2, 0), (1, 1), (0, 2), (0, 3)]
    assert rolling_plan(5, 2, 0) == [(3, 0), (1, 2), (0, 4), (0, 5)]
    with pytest.raises(ValueError):
        rolling_plan(3, 0, 0)


def test_e4a_invariants():
    for n in range(1, 7):
        for mu in range(0, n + 1):
            for ms in range(0, 3):
                if mu == ms == 0:
                    continue
                for old, new in rolling_plan(n, mu, ms):
                    assert old + new >= n - mu and old + new <= n + ms and new <= n


def test_e4b():
    assert ready_ticks([[True, True, False, True, True, True], [False, True, True], [True, False]], 2) == [1, 2, None]
    assert ready_ticks([[True]], 1) == [0]


def test_e4c():
    assert rollback_plan(4, 1, 1, (2, 1)) == [(4, 0)]
    assert rollback_plan(3, 0, 1, (1, 2)) == [(2, 1), (3, 0)]
    assert rollback_plan(3, 1, 0, (0, 3)) == [(0, 2), (1, 1), (2, 0), (3, 0)]


DF = ["FROM python:3.12-slim", "WORKDIR /app", "COPY requirements.txt .", "RUN pip install -r requirements.txt",
      "COPY app/ ./app", 'CMD ["python", "-m", "app"]']


def test_e5():
    assert rebuilt_from(DF, ["app/main.py"]) == 4
    assert rebuilt_from(DF, ["requirements.txt", "app/x.py"]) == 2
    assert rebuilt_from(DF, ["README.md"]) is None
    assert rebuilt_from(DF, [], base_changed=True) == 0
    assert rebuilt_from(["FROM x", "COPY . /src"], ["README.md"]) == 1
    assert rebuilt_from(["FROM x", "COPY --chown=app *.py /src/"], ["a.py"]) == 1
    assert rebuilt_from(["FROM x", "COPY --chown=app *.py /src/"], ["sub/a.txt"]) is None
