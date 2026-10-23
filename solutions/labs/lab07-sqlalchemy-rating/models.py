"""Модели базы рейтинга: игроки и матчи (SQLAlchemy 2, стиль Mapped)."""
from datetime import datetime

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

START_RATING = 1000
RESULTS = ("win1", "win2", "draw")


class Base(DeclarativeBase):
    pass


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    name: Mapped[str] = mapped_column(String(64))
    rating: Mapped[int] = mapped_column(default=START_RATING, server_default=str(START_RATING))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class Match(Base):
    __tablename__ = "matches"
    __table_args__ = (
        CheckConstraint("result IN ('win1', 'win2', 'draw')", name="ck_matches_result"),
        CheckConstraint("player1_id <> player2_id", name="ck_matches_two_players"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    game: Mapped[str] = mapped_column(String(32))
    player1_id: Mapped[int] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), index=True)
    player2_id: Mapped[int] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), index=True)
    result: Mapped[str] = mapped_column(String(8))
    delta1: Mapped[int]
    delta2: Mapped[int]
    played_at: Mapped[datetime] = mapped_column(server_default=func.now(), index=True)
