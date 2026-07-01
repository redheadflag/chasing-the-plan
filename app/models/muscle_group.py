from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.exercise import Exercise


class MuscleGroup(TimestampMixin, Base):
    __tablename__ = "muscle_group"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    position: Mapped[int] = mapped_column(Integer, default=0)

    exercises: Mapped[list["Exercise"]] = relationship(
        back_populates="muscle_group",
        cascade="all, delete-orphan",
        order_by="Exercise.name",
    )
