from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.muscle_group import MuscleGroupOut


class ExerciseBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    url: str | None = Field(default=None, max_length=1000)
    muscle_group_id: int


class ExerciseCreate(ExerciseBase):
    pass


class ExerciseUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    url: str | None = Field(default=None, max_length=1000)
    muscle_group_id: int | None = None
    archived: bool | None = None


class ExerciseOut(ExerciseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    archived: bool
    muscle_group: MuscleGroupOut | None = None


# --- Bulk import (used by the generated seed .http file) ---


class ExerciseBulkItem(BaseModel):
    """One exercise in a bulk import; the muscle group is referenced by name."""

    muscle_group: str = Field(min_length=1, max_length=120)
    name: str = Field(min_length=1, max_length=200)
    url: str | None = Field(default=None, max_length=1000)


class ExerciseBulkCreate(BaseModel):
    # Create any muscle groups referenced but not yet present.
    create_missing_groups: bool = True
    items: list[ExerciseBulkItem]


class ExerciseBulkResult(BaseModel):
    created_groups: int
    created_exercises: int
    skipped_existing: int
    # URLs backfilled into exercises that already existed without one.
    updated_urls: int = 0
