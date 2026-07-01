from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class MuscleGroupBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    position: int = 0


class MuscleGroupCreate(MuscleGroupBase):
    pass


class MuscleGroupUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    position: int | None = None


class MuscleGroupOut(MuscleGroupBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
