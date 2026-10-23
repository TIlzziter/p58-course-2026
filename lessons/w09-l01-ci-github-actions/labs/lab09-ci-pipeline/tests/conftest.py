from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent.parent


@pytest.fixture
def ci_text() -> str:
    return (HERE / "sample" / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
