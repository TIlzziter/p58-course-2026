"""Модели базы рейтинга: игроки и матчи (SQLAlchemy 2, стиль Mapped).

Задача 1: колонки уже есть, но схема не защищает данные. Добавьте ограничения — см. README.
"""
from datetime import datetime

from sqlalchemy import BigInteger, ForeignKey, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

START_RATING = 1000
RESULTS = ("win1", "win2", "draw")


class Base(DeclarativeBase):
    pass


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)                    # TODO: один игрок Telegram — одна строка
    name: Mapped[str] = mapped_column(String(64))
    rating: Mapped[int]                                                # TODO: стартовый рейтинг 1000 (и в базе тоже)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class Match(Base):
    __tablename__ = "matches"
    # TODO: CHECK на result (только win1/win2/draw) и на то, что игроки разные

    id: Mapped[int] = mapped_column(primary_key=True)
    game: Mapped[str] = mapped_column(String(32))
    player1_id: Mapped[int] = mapped_column(ForeignKey("players.id"))  # TODO: каскадное удаление, индекс
    player2_id: Mapped[int] = mapped_column(ForeignKey("players.id"))
    result: Mapped[str] = mapped_column(String(8))
    delta1: Mapped[int]
    delta2: Mapped[int]
    played_at: Mapped[datetime] = mapped_column(server_default=func.now())   # TODO: индекс — история сортируется по нему
