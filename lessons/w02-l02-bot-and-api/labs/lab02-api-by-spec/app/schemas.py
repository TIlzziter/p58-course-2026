"""Модели запросов. TODO (задачи 2 и 4): добавьте ограничения из SPEC.md через Field(...)."""
from pydantic import BaseModel


class RoomCreate(BaseModel):
    player: str


class JoinIn(BaseModel):
    player: str


class MoveIn(BaseModel):
    player: str
    cell: int
