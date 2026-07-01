from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import MuscleGroup
from app.schemas.muscle_group import MuscleGroupCreate, MuscleGroupUpdate


def list_muscle_groups(db: Session) -> list[MuscleGroup]:
    stmt = select(MuscleGroup).order_by(MuscleGroup.position, MuscleGroup.name)
    return list(db.scalars(stmt))


def get_muscle_group(db: Session, group_id: int) -> MuscleGroup | None:
    return db.get(MuscleGroup, group_id)


def create_muscle_group(db: Session, data: MuscleGroupCreate) -> MuscleGroup:
    group = MuscleGroup(name=data.name, position=data.position)
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


def update_muscle_group(
    db: Session, group: MuscleGroup, data: MuscleGroupUpdate
) -> MuscleGroup:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(group, field, value)
    db.commit()
    db.refresh(group)
    return group


def delete_muscle_group(db: Session, group: MuscleGroup) -> None:
    db.delete(group)
    db.commit()
