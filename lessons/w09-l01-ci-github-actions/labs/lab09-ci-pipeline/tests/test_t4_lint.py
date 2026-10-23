from ci_tools import lint_workflow, load_workflow

GOOD = """
on: [push]
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup
      - run: pytest
        env:
          TOKEN: ${{ secrets.TOKEN }}
"""


def lint(text):
    return lint_workflow(load_workflow(text))


def test_good_is_clean():
    assert lint(GOOD) == []


def test_unpinned():
    text = GOOD.replace("actions/checkout@v4", "actions/checkout@main")
    assert lint(text) == ["unpinned:actions/checkout@main"]
    assert lint(GOOD.replace("actions/checkout@v4", "actions/checkout")) == ["unpinned:actions/checkout"]
    sha = "actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683"
    assert lint(GOOD.replace("actions/checkout@v4", sha)) == []


def test_permissions_top_or_every_job():
    no_top = GOOD.replace("permissions:\n  contents: read\n", "")
    assert lint(no_top) == ["no_permissions:test"]
    per_job = no_top.replace("    timeout-minutes: 5\n", "    timeout-minutes: 5\n    permissions: {}\n")
    assert lint(per_job) == []


def test_timeout():
    assert lint(GOOD.replace("    timeout-minutes: 5\n", "")) == ["no_timeout:test"]


def test_secret_in_run():
    text = GOOD.replace("- run: pytest", '- run: echo ${{ secrets.TOKEN }} | docker login -u bot --password-stdin')
    assert lint(text) == ["secret_in_run:test"]


def test_float_version():
    text = GOOD.replace("    steps:", "    strategy:\n      matrix:\n        py: [3.12, 3.10]\n    steps:")
    assert lint(text) == ["float_version:test"]
    ok = GOOD.replace("    steps:", '    strategy:\n      matrix:\n        py: ["3.12", "3.10"]\n    steps:')
    assert lint(ok) == []


def test_pr_target_checkout():
    text = GOOD.replace("on: [push]", "on: [pull_request_target]").replace(
        "- uses: actions/checkout@v4",
        "- uses: actions/checkout@v4\n        with:\n          ref: ${{ github.event.pull_request.head.sha }}")
    assert lint(text) == ["pr_target_checkout:test"]
    # тот же checkout на обычном pull_request — не опасен
    assert lint(text.replace("pull_request_target", "pull_request")) == []


def test_order_jobs_then_steps():
    text = """
on: push
jobs:
  a:
    steps:
      - uses: x/y
  b:
    timeout-minutes: 1
    steps:
      - run: echo ${{ secrets.S }}
"""
    assert lint(text) == ["no_permissions:a", "no_timeout:a", "unpinned:x/y",
                          "no_permissions:b", "secret_in_run:b"]
