"""История партий в БД."""
from sqlalchemy import String, delete, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class Match(Base):
    __tablename__ = "matches"
    id: Mapped[int] = mapped_column(primary_key=True)
    room: Mapped[str] = mapped_column(String(16))
    winner: Mapped[str] = mapped_column(String(64))
    score: Mapped[int]
    finished_at: Mapped[int]             # unix-время, секунды


class MatchRepo:
    def __init__(self, session: Session):
        self.s = session

    def add(self, room: str, winner: str, score: int, finished_at: int) -> int:
        m = Match(room=room, winner=winner, score=score, finished_at=finished_at)
        self.s.add(m)
        self.s.flush()
        return m.id

    def top_winners(self, n: int) -> list[tuple[str, int]]:
        """n игроков с наибольшим числом побед: (имя, побед), при равенстве — по имени."""
        wins = func.count(Match.id).label("wins")
        q = select(Match.winner, wins).group_by(Match.winner).order_by(wins.desc(), Match.winner).limit(n)
        return [(w, c) for w, c in self.s.execute(q)]

    def history(self, room: str, limit: int = 10) -> list[tuple[str, int]]:
        """Последние партии комнаты, новые сначала: (победитель, счёт)."""
        q = (select(Match.winner, Match.score).where(Match.room == room)
             .order_by(Match.finished_at.desc(), Match.id.desc()).limit(limit))
        return [(w, sc) for w, sc in self.s.execute(q)]

    def delete_older(self, ts: int) -> int:
        """Удалить партии, закончившиеся строго раньше ts. Вернуть, сколько удалено."""
        res = self.s.execute(delete(Match).where(Match.finished_at < ts))
        return res.rowcount
