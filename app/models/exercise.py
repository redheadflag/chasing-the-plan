from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.muscle_group import MuscleGroup


class Exercise(TimestampMixin, Base):
    __tablename__ = "exercise"
    __table_args__ = (
        UniqueConstraint("muscle_group_id", "name", name="uq_exercise_group_name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    muscle_group_id: Mapped[int] = mapped_column(
        ForeignKey("muscle_group.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(200))
    url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    archived: Mapped[bool] = mapped_column(Boolean, default=False)

    muscle_group: Mapped["MuscleGroup"] = relationship(back_populates="exercises")
