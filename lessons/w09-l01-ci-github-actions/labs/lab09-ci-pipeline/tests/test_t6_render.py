import pytest
from ci_tools import render

CTX = {
    "matrix": {"python-version": "3.13", "os": "linux"},
    "github": {"ref_name": "main", "sha": "abc123", "event": {"pull_request": {"number": 7}}},
    "env": {"DEBUG": True},
}


@pytest.mark.parametrize("text, out", [
    ("python ${{ matrix.python-version }}", "python 3.13"),
    ("${{matrix.os}}-${{ github.ref_name }}", "linux-main"),
    ("pr-${{ github.event.pull_request.number }}", "pr-7"),
    ("tag:${{ github.sha }}", "tag:abc123"),
    ("no expr here", "no expr here"),
    ("[${{ matrix.missing }}]", "[]"),
    ("${{ github.nope.deeper }}", ""),
    ("${{ matrix.arch || 'x64' }}", "x64"),
    ("${{ matrix.os || 'x64' }}", "linux"),
    ("${{ env.DEBUG }}", "true"),
    ("${{ matrix.a || matrix.os || 'z' }}", "linux"),
])
def test_render(text, out):
    assert render(text, CTX) == out
