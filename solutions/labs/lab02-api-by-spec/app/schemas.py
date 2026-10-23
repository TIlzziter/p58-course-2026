"""Модели запросов (эталон): ограничения из SPEC.md прямо в моделях."""
from pydantic import BaseModel, Field

Name = Field(min_length=1, max_length=20, pattern=r"^\S(.*\S)?$")


class RoomCreate(BaseModel):
    player: str = Name


class JoinIn(BaseModel):
    player: str = Name


class MoveIn(BaseModel):
    player: str = Name
    cell: int = Field(ge=0, le=8)
