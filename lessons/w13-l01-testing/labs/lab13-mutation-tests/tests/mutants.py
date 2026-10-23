"""Мутанты: маленькие правки кода из game/. Хороший набор тестов должен «убить» (уронить) каждого.

Формат: модуль → [(описание, что заменить, на что)]. Подглядывать можно, но честнее сначала написать тесты
по docstring, а потом смотреть, кто выжил.
"""

MUTANTS = {
    "scoring": [
        ("граница числа игроков", "if not 2 <= players <= 4:", "if not 2 <= players <= 5:"),
        ("нулевое место", "if place < 1 or place > players:", "if place < 0 or place > players:"),
        ("бонус победителя", "return base + 2 if place == 1 else base", "return base + 1 if place == 1 else base"),
        ("порог серии", "if n < 3:", "if n <= 3:"),
        ("потолок бонуса", "min((n - 2) * 5, 25)", "min((n - 2) * 5, 30)"),
        ("серия с начала, а не с конца", "for won in reversed(results):", "for won in results:"),
        ("ничья не принимается", "if score_a not in (0, 0.5, 1):", "if score_a not in (0, 1):"),
        ("масштаб Эло", "10 ** ((rb - ra) / 400)", "10 ** ((rb - ra) / 200)"),
        ("коэффициент k игнорируется", "delta = k * (score_a - expected_a)", "delta = 32 * (score_a - expected_a)"),
        ("округление вниз", "return round(ra + delta), round(rb - delta)", "return int(ra + delta), int(rb - delta)"),
    ],
    "rooms": [
        ("повторный вход", "if user in self.players:\n            return False", "if False:\n            return False"),
        ("вместимость", "if len(self.players) >= self.capacity:", "if len(self.players) > self.capacity:"),
        ("вместимость по умолчанию", "capacity: int = 4", "capacity: int = 5"),
        ("хост — последний", "return self.players[0] if self.players else None",
         "return self.players[-1] if self.players else None"),
        ("готовность не снимается", "self.players.remove(user)\n        self.ready.discard(user)",
         "self.players.remove(user)"),
        ("один игрок может стартовать", "len(self.players) >= 2 and", "len(self.players) >= 1 and"),
        ("any вместо all", "all(p in self.ready for p in self.players)", "any(p in self.ready for p in self.players)"),
        ("снять готовность нельзя", "        else:\n            self.ready.discard(user)", "        else:\n            pass"),
        ("готовность у чужого", "    def set_ready(self, user: str, value: bool = True) -> None:\n        if user not in self.players:\n            raise NotInRoom(user)",
         "    def set_ready(self, user: str, value: bool = True) -> None:\n        if False:\n            raise NotInRoom(user)"),
    ],
    "matchmaker": [
        ("группа на одного больше", "if len(self.queue) >= self.size:", "if len(self.queue) > self.size:"),
        ("обратный порядок", "names = [u for u, _ in group]", "names = [u for u, _ in reversed(group)]"),
        ("таймаут не убирает из очереди", "            self.cancel(user)\n            raise", "            raise"),
        ("дубликаты разрешены", "if user in self.waiting():", "if False:"),
        ("cancel всегда True", "return len(self.queue) < before", "return True"),
    ],
    "app": [
        ("hello не проверяется", 'if hello.get("type") == "hello" else ""', 'if True else ""'),
        ("имя из пробелов", 'str(hello.get("name", "")).strip()', 'str(hello.get("name", ""))'),
        ("занятое имя", "if name in room:", "if False:"),
        ("граница длины", "if len(text) > MAX_TEXT:", "if len(text) >= MAX_TEXT:"),
        ("ошибка уходит всем", 'await ws.send_json({"type": "error", "reason": "too_long"})',
         'await broadcast(code, {"type": "error", "reason": "too_long"})'),
        ("пробелы не убираются", 'text = str(msg.get("text", "")).strip()', 'text = str(msg.get("text", ""))'),
        ("пустое сообщение уходит", "if not text:\n                    continue", "if False:\n                    continue"),
        ("нет left", '            await broadcast(code, {"type": "left", "name": name, "players": sorted(room)})',
         "            pass"),
        ("комнаты общие", "room = rooms.setdefault(code, {})", 'room = rooms.setdefault("all", {})\n        code = "all"'),
    ],
    "repo": [
        ("топ по возрастанию", "order_by(wins.desc(), Match.winner)", "order_by(wins, Match.winner)"),
        ("ничьи в топе не по имени", "order_by(wins.desc(), Match.winner)", "order_by(wins.desc(), Match.winner.desc())"),
        ("история старые сначала", "order_by(Match.finished_at.desc(), Match.id.desc())",
         "order_by(Match.finished_at, Match.id)"),
        ("одновременные партии", "order_by(Match.finished_at.desc(), Match.id.desc())",
         "order_by(Match.finished_at.desc(), Match.id)"),
        ("лимит на один больше", ".limit(limit))", ".limit(limit + 1))"),
        ("история всех комнат", ".where(Match.room == room)", ".where(Match.room != '')"),
        ("удаляет и ровно ts", "Match.finished_at < ts", "Match.finished_at <= ts"),
        ("топ без лимита", ".order_by(wins.desc(), Match.winner).limit(n)", ".order_by(wins.desc(), Match.winner)"),
    ],
}
