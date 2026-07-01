from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.exercise import Exercise
    from app.models.plan_exercise import PlanExercise
    from app.models.workout_block import WorkoutBlock


class PlanUnit(TimestampMixin, Base):
    """One exercise placement in a workout, holding an ordered list of set-stages."""

    __tablename__ = "plan_unit"

    id: Mapped[int] = mapped_column(primary_key=True)
    block_id: Mapped[int] = mapped_column(
        ForeignKey("workout_block.id", ondelete="CASCADE"), index=True
    )
    exercise_id: Mapped[int] = mapped_column(
        ForeignKey("exercise.id", ondelete="RESTRICT"), index=True
    )
    position: Mapped[int] = mapped_column(Integer, default=0)
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Green "film this" marker seen in the sample plan.
    highlight: Mapped[bool] = mapped_column(Boolean, default=False)

    block: Mapped["WorkoutBlock"] = relationship(back_populates="units")
    exercise: Mapped["Exercise"] = relationship()
    entries: Mapped[list["PlanExercise"]] = relationship(
        back_populates="unit",
        cascade="all, delete-orphan",
        order_by="PlanExercise.position",
    )
