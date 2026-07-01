from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import BlockType, DayOfWeek, PlanExerciseKind, WorkoutKind
from app.schemas.exercise import ExerciseOut

# --------------------------------------------------------------------------- #
# Input schemas (nested create / replace)
# --------------------------------------------------------------------------- #


class PlanExerciseIn(BaseModel):
    kind: PlanExerciseKind
    sets: int = Field(ge=1)
    reps: int | None = Field(default=None, ge=1)
    weight: Decimal | None = Field(default=None, ge=0)
    duration_seconds: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def _check_kind_fields(self) -> "PlanExerciseIn":
        if self.kind is PlanExerciseKind.WEIGHT and self.reps is None:
            raise ValueError("weight-based set-stage requires 'reps'")
        if self.kind is PlanExerciseKind.TIME and self.duration_seconds is None:
            raise ValueError("time-based set-stage requires 'duration_seconds'")
        return self


class PlanUnitIn(BaseModel):
    exercise_id: int
    note: str | None = Field(default=None, max_length=255)
    highlight: bool = False
    entries: list[PlanExerciseIn] = Field(min_length=1)


class WorkoutBlockIn(BaseModel):
    block_type: BlockType = BlockType.SINGLE
    note: str | None = Field(default=None, max_length=255)
    units: list[PlanUnitIn] = Field(min_length=1)

    @model_validator(mode="after")
    def _check_single_block(self) -> "WorkoutBlockIn":
        if self.block_type is BlockType.SINGLE and len(self.units) != 1:
            raise ValueError("a SINGLE block must contain exactly one plan unit")
        return self


class WorkoutCreate(BaseModel):
    athlete_id: int
    name: str = Field(min_length=1, max_length=200)
    day_of_week: DayOfWeek
    kind: WorkoutKind = WorkoutKind.ORDINARY
    position: int = 0
    notes: str | None = None
    blocks: list[WorkoutBlockIn] = Field(default_factory=list)


class WorkoutReplace(BaseModel):
    """Full replacement of a workout's contents (athlete stays fixed)."""

    name: str = Field(min_length=1, max_length=200)
    day_of_week: DayOfWeek
    kind: WorkoutKind = WorkoutKind.ORDINARY
    position: int = 0
    notes: str | None = None
    blocks: list[WorkoutBlockIn] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# Output schemas
# --------------------------------------------------------------------------- #


class PlanExerciseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    position: int
    kind: PlanExerciseKind
    sets: int
    reps: int | None
    weight: Decimal | None
    duration_seconds: int | None


class PlanUnitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    position: int
    exercise_id: int
    note: str | None
    highlight: bool
    exercise: ExerciseOut
    entries: list[PlanExerciseOut]


class WorkoutBlockOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    position: int
    block_type: BlockType
    note: str | None
    units: list[PlanUnitOut]


class WorkoutOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    athlete_id: int
    name: str
    day_of_week: DayOfWeek
    kind: WorkoutKind
    position: int
    notes: str | None
    blocks: list[WorkoutBlockOut]


class WorkoutSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    athlete_id: int
    name: str
    day_of_week: DayOfWeek
    kind: WorkoutKind
    position: int
