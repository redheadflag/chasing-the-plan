from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin
from app.models.enums import PlanExerciseKind

if TYPE_CHECKING:
    from app.models.plan_unit import PlanUnit


class PlanExercise(TimestampMixin, Base):
    """A single set-stage within a plan unit (weight-based or time-based)."""

    __tablename__ = "plan_exercise"
    __table_args__ = (
        CheckConstraint(
            "(kind = 'WEIGHT' AND reps IS NOT NULL) "
            "OR (kind = 'TIME' AND duration_seconds IS NOT NULL)",
            name="ck_plan_exercise_kind_fields",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    plan_unit_id: Mapped[int] = mapped_column(
        ForeignKey("plan_unit.id", ondelete="CASCADE"), index=True
    )
    position: Mapped[int] = mapped_column(Integer, default=0)
    kind: Mapped[PlanExerciseKind] = mapped_column(
        SAEnum(PlanExerciseKind, name="plan_exercise_kind")
    )
    sets: Mapped[int] = mapped_column(Integer)
    reps: Mapped[int | None] = mapped_column(Integer, nullable=True)
    weight: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    unit: Mapped["PlanUnit"] = relationship(back_populates="entries")
