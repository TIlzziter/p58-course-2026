from pathlib import Path

EX = Path(__file__).resolve().parent.parent / "examples"


def ex(name: str) -> str:
    return (EX / name).read_text(encoding="utf-8")
