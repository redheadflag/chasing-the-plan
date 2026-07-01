from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.workout import Workout


class Athlete(TimestampMixin, Base):
    __tablename__ = "athlete"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    workouts: Mapped[list["Workout"]] = relationship(
        back_populates="athlete",
        cascade="all, delete-orphan",
        order_by="Workout.position",
    )
