from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AthleteBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    note: str | None = None


class AthleteCreate(AthleteBase):
    pass


class AthleteUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    note: str | None = None


class AthleteOut(AthleteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
