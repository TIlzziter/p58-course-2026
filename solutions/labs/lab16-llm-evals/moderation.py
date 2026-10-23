"""Задача 3. Простая модерация текста игроков до и после модели."""
import re

LEET = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "@": "a", "$": "s", "ё": "е"})


def normalize(word: str) -> str:
    """Нижний регистр, замены LEET, убрать всё, кроме букв, сжать повторы букв подряд до одной."""
    w = word.lower().translate(LEET)
    w = "".join(ch for ch in w if ch.isalpha())
    return re.sub(r"(.)\1+", r"\1", w)


def moderate(text: str, banned: set[str]) -> list[str]:
    """Какие слова из banned встречаются в тексте (ответ — слова в том виде, как они записаны
    в banned, по алфавиту, без повторов).

    Слова текста разделены пробелами. Слово совпадает, если normalize(слово) == normalize(запрещённого).
    Хитрость «по букве через пробел»: подряд идущие слова из одного символа склеиваем в одно слово
    («b a d» → «bad»). Подстроки не ищем: «class» не содержит запрещённого «ass».
    """
    targets = {normalize(b): b for b in banned}
    words: list[str] = []
    singles: list[str] = []
    for tok in text.split():
        n = normalize(tok)
        if len(n) == 1 and len(tok) <= 2:
            singles.append(n)
            continue
        if singles:
            words.append(normalize("".join(singles)))
            singles = []
        words.append(n)
    if singles:
        words.append(normalize("".join(singles)))
    return sorted({targets[w] for w in words if w in targets})
