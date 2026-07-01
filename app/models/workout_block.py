from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin
from app.models.enums import BlockType

if TYPE_CHECKING:
    from app.models.plan_unit import PlanUnit
    from app.models.workout import Workout


class WorkoutBlock(TimestampMixin, Base):
    __tablename__ = "workout_block"

    id: Mapped[int] = mapped_column(primary_key=True)
    workout_id: Mapped[int] = mapped_column(
        ForeignKey("workout.id", ondelete="CASCADE"), index=True
    )
    block_type: Mapped[BlockType] = mapped_column(
        SAEnum(BlockType, name="block_type"), default=BlockType.SINGLE
    )
    position: Mapped[int] = mapped_column(Integer, default=0)
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)

    workout: Mapped["Workout"] = relationship(back_populates="blocks")
    units: Mapped[list["PlanUnit"]] = relationship(
        back_populates="block",
        cascade="all, delete-orphan",
        order_by="PlanUnit.position",
    )
