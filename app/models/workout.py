from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin
from app.models.enums import DayOfWeek, WorkoutKind

if TYPE_CHECKING:
    from app.models.athlete import Athlete
    from app.models.workout_block import WorkoutBlock


class Workout(TimestampMixin, Base):
    __tablename__ = "workout"

    id: Mapped[int] = mapped_column(primary_key=True)
    athlete_id: Mapped[int] = mapped_column(
        ForeignKey("athlete.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(200))
    week: Mapped[int] = mapped_column(
        Integer, default=1, server_default="1", index=True
    )
    day_of_week: Mapped[DayOfWeek] = mapped_column(
        SAEnum(DayOfWeek, name="day_of_week")
    )
    kind: Mapped[WorkoutKind] = mapped_column(
        SAEnum(WorkoutKind, name="workout_kind"), default=WorkoutKind.ORDINARY
    )
    position: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    athlete: Mapped["Athlete"] = relationship(back_populates="workouts")
    blocks: Mapped[list["WorkoutBlock"]] = relationship(
        back_populates="workout",
        cascade="all, delete-orphan",
        order_by="WorkoutBlock.position",
    )
