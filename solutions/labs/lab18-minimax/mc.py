"""Монте-Карло: случайные доигрывания и UCT (задачи 6–7)."""
import math
import random


def random_playout(game, s, rng: random.Random) -> int:
    """Задача 6. Доиграть случайными ходами (rng.choice(game.moves(s))) до конца; вернуть winner."""
    while (w := game.winner(s)) is None:
        s = game.play(s, rng.choice(game.moves(s)))
    return w


def mc_move(game, s, playouts: int, rng: random.Random):
    """Задача 6. «Плоский» Монте-Карло: для каждого хода по порядку moves() — playouts доигрываний.
    Очки хода — победы ходящего + 0.5 · ничьи. Ход, который сразу выигрывает, берём без доигрываний.
    Лучший — с наибольшими очками, при равенстве — первый."""
    p = game.to_move(s)
    best, best_score = None, -1.0
    for m in game.moves(s):
        nxt = game.play(s, m)
        if game.winner(nxt) == p:
            return m
        score = 0.0
        for _ in range(playouts):
            w = random_playout(game, nxt, rng)
            score += 1.0 if w == p else 0.5 if w == 0 else 0.0
        if score > best_score:
            best, best_score = m, score
    return best


class Node:
    __slots__ = ("state", "parent", "move", "children", "untried", "visits", "wins")

    def __init__(self, game, state, parent=None, move=None):
        self.state, self.parent, self.move = state, parent, move
        self.children: list[Node] = []
        self.untried = list(game.moves(state))
        self.visits = 0
        self.wins = 0.0  # очки игрока, который сделал ход move (то есть -to_move(state))


def uct_select(node: "Node", c: float) -> "Node":
    """Потомок с максимальным wins/visits + c·√(ln N / visits); при равенстве — первый."""
    log_n = math.log(node.visits)
    return max(node.children, key=lambda ch: ch.wins / ch.visits + c * math.sqrt(log_n / ch.visits))


def mcts_move(game, s, iterations: int, rng: random.Random, c: float = 1.4):
    """Задача 7*. UCT: выбор (uct_select, пока нет неиспробованных ходов) → расширение (ход
    untried.pop(rng.randrange(len(untried)))) → доигрывание random_playout → обратный проход: каждому
    узлу на пути visits += 1, wins += 1 за победу игрока, сделавшего ход в узел, 0.5 за ничью.
    Ответ — ход самого посещаемого потомка корня."""
    root = Node(game, s)
    for _ in range(iterations):
        node = root
        while not node.untried and node.children:
            node = uct_select(node, c)
        if node.untried:
            m = node.untried.pop(rng.randrange(len(node.untried)))
            child = Node(game, game.play(node.state, m), node, m)
            node.children.append(child)
            node = child
        w = random_playout(game, node.state, rng)
        while node is not None:
            node.visits += 1
            mover = -game.to_move(node.state)
            node.wins += 1.0 if w == mover else 0.5 if w == 0 else 0.0
            node = node.parent
    return max(root.children, key=lambda ch: ch.visits).move
