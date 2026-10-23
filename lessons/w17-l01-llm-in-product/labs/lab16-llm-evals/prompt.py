"""Задача 1. Сообщения для модели: роли, история, текст игрока отдельно от инструкций."""

OPEN, CLOSE = "<player_text>", "</player_text>"


def wrap_player_text(text: str) -> str:
    """Текст игрока в тегах. Сами теги из текста вырезаем, чтобы игрок не мог «закрыть» блок раньше."""
    # TODO: вырезать теги OPEN и CLOSE из текста игрока
    return f"{OPEN}\n{text}\n{CLOSE}"


def build_messages(system: str, history: list[dict], user_text: str, budget: int) -> list[dict]:
    """Список сообщений [{"role": ..., "content": ...}]: system, затем история, затем текст игрока
    (через wrap_player_text) с ролью user.

    budget — максимум символов в сумме по всем content. Если не влезает — выбрасываем самые старые
    сообщения истории парами (user + assistant), пока не влезет. system и текущее сообщение не трогаем;
    если не влезают даже они — ValueError. history не меняем.
    """
    current = {"role": "user", "content": wrap_player_text(user_text)}
    head = {"role": "system", "content": system}
    hist = list(history)

    def size():
        return len(head["content"]) + len(current["content"]) + sum(len(m["content"]) for m in hist)

    # TODO: выбрасывать парами; ValueError, если не влезает даже без истории
    while hist and size() > budget:
        hist = hist[1:]
    return [head, *hist, current]
