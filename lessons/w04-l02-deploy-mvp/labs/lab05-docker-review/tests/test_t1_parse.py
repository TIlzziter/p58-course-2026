from conftest import ex
from review import parse_dockerfile


def test_good_dockerfile():
    instrs = parse_dockerfile(ex("Dockerfile.good"))
    assert [i for i, _ in instrs] == ["FROM", "WORKDIR", "COPY", "RUN", "COPY", "RUN", "USER", "EXPOSE", "CMD"]
    assert instrs[0] == ("FROM", "python:3.12-slim")
    assert instrs[3] == ("RUN", "pip install --no-cache-dir -r requirements.txt")


def test_lowercase_and_indented_comment():
    text = "from python:3.12\n   # комментарий с отступом\nrun echo hi\n\n"
    assert parse_dockerfile(text) == [("FROM", "python:3.12"), ("RUN", "echo hi")]


def test_multiple_continuations():
    text = "RUN apt-get update && \\\n    apt-get install -y curl \\\n    && rm -rf /var/lib/apt/lists/*\n"
    assert parse_dockerfile(text) == [("RUN", "apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*")]
