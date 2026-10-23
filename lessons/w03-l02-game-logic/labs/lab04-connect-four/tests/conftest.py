def board_from(text: str) -> list[list[int]]:
    """Поле из картинки: строки сверху вниз, '.' — пусто, 'x' — игрок 1, 'o' — игрок 2."""
    m = {".": 0, "x": 1, "o": 2}
    return [[m[ch] for ch in line.strip()] for line in text.strip().splitlines()]
