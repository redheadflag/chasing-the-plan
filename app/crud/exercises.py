from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Exercise, MuscleGroup
from app.schemas.exercise import (
    ExerciseBulkCreate,
    ExerciseBulkResult,
    ExerciseCreate,
    ExerciseUpdate,
)


def list_exercises(
    db: Session,
    muscle_group_id: int | None = None,
    q: str | None = None,
    include_archived: bool = False,
) -> list[Exercise]:
    stmt = select(Exercise).options(selectinload(Exercise.muscle_group))
    if muscle_group_id is not None:
        stmt = stmt.where(Exercise.muscle_group_id == muscle_group_id)
    if q:
        stmt = stmt.where(Exercise.name.ilike(f"%{q}%"))
    if not include_archived:
        stmt = stmt.where(Exercise.archived.is_(False))
    stmt = stmt.order_by(Exercise.name)
    return list(db.scalars(stmt))


def get_exercise(db: Session, exercise_id: int) -> Exercise | None:
    stmt = (
        select(Exercise)
        .where(Exercise.id == exercise_id)
        .options(selectinload(Exercise.muscle_group))
    )
    return db.scalars(stmt).first()


def create_exercise(db: Session, data: ExerciseCreate) -> Exercise:
    exercise = Exercise(
        muscle_group_id=data.muscle_group_id, name=data.name, url=data.url
    )
    db.add(exercise)
    db.commit()
    return get_exercise(db, exercise.id)


def update_exercise(db: Session, exercise: Exercise, data: ExerciseUpdate) -> Exercise:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(exercise, field, value)
    db.commit()
    return get_exercise(db, exercise.id)


def delete_exercise(db: Session, exercise: Exercise) -> None:
    db.delete(exercise)
    db.commit()


def bulk_create_exercises(
    db: Session, data: ExerciseBulkCreate
) -> ExerciseBulkResult:
    """Idempotent bulk import: creates missing groups/exercises, skips duplicates."""
    groups: dict[str, MuscleGroup] = {
        g.name: g for g in db.scalars(select(MuscleGroup))
    }
    created_groups = 0
    created_exercises = 0
    skipped = 0
    updated_urls = 0

    for item in data.items:
        group = groups.get(item.muscle_group)
        if group is None:
            if not data.create_missing_groups:
                skipped += 1
                continue
            group = MuscleGroup(name=item.muscle_group, position=len(groups))
            db.add(group)
            db.flush()
            groups[item.muscle_group] = group
            created_groups += 1

        existing = db.scalar(
            select(Exercise).where(
                Exercise.muscle_group_id == group.id, Exercise.name == item.name
            )
        )
        if existing:
            # Backfill a URL onto an existing exercise that lacks one.
            if item.url and not existing.url:
                existing.url = item.url
                updated_urls += 1
            else:
                skipped += 1
            continue

        db.add(Exercise(muscle_group_id=group.id, name=item.name, url=item.url))
        created_exercises += 1

    db.commit()
    return ExerciseBulkResult(
        created_groups=created_groups,
        created_exercises=created_exercises,
        skipped_existing=skipped,
        updated_urls=updated_urls,
    )
