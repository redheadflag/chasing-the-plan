from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Exercise, PlanExercise, PlanUnit, Workout, WorkoutBlock
from app.schemas.workout import WorkoutBlockIn, WorkoutCreate, WorkoutReplace


def _workout_loaders():
    """Eager-load the full workout tree for output/report rendering."""
    return [
        selectinload(Workout.blocks)
        .selectinload(WorkoutBlock.units)
        .selectinload(PlanUnit.entries),
        selectinload(Workout.blocks)
        .selectinload(WorkoutBlock.units)
        .selectinload(PlanUnit.exercise)
        .selectinload(Exercise.muscle_group),
    ]


def _build_blocks(blocks_in: list[WorkoutBlockIn]) -> list[WorkoutBlock]:
    """Turn nested input schemas into an ORM block tree, assigning positions by order."""
    blocks: list[WorkoutBlock] = []
    for b_idx, b in enumerate(blocks_in):
        units: list[PlanUnit] = []
        for u_idx, u in enumerate(b.units):
            entries = [
                PlanExercise(
                    position=e_idx,
                    kind=e.kind,
                    sets=e.sets,
                    reps=e.reps,
                    weight=e.weight,
                    duration_seconds=e.duration_seconds,
                )
                for e_idx, e in enumerate(u.entries)
            ]
            units.append(
                PlanUnit(
                    position=u_idx,
                    exercise_id=u.exercise_id,
                    note=u.note,
                    highlight=u.highlight,
                    entries=entries,
                )
            )
        blocks.append(
            WorkoutBlock(
                position=b_idx, block_type=b.block_type, note=b.note, units=units
            )
        )
    return blocks


def list_workouts_for_athlete(db: Session, athlete_id: int) -> list[Workout]:
    stmt = (
        select(Workout)
        .where(Workout.athlete_id == athlete_id)
        .order_by(Workout.week, Workout.position, Workout.id)
    )
    return list(db.scalars(stmt))


def get_workout(db: Session, workout_id: int) -> Workout | None:
    stmt = (
        select(Workout).where(Workout.id == workout_id).options(*_workout_loaders())
    )
    return db.scalars(stmt).first()


def get_athlete_plan(db: Session, athlete_id: int) -> list[Workout]:
    """All of an athlete's workouts, fully loaded and ordered, for report rendering."""
    stmt = (
        select(Workout)
        .where(Workout.athlete_id == athlete_id)
        .order_by(Workout.week, Workout.position, Workout.id)
        .options(*_workout_loaders())
    )
    return list(db.scalars(stmt))


def create_workout(db: Session, data: WorkoutCreate) -> Workout:
    workout = Workout(
        athlete_id=data.athlete_id,
        name=data.name,
        week=data.week,
        day_of_week=data.day_of_week,
        kind=data.kind,
        position=data.position,
        notes=data.notes,
        blocks=_build_blocks(data.blocks),
    )
    db.add(workout)
    db.commit()
    return get_workout(db, workout.id)


def replace_workout(
    db: Session, workout: Workout, data: WorkoutReplace
) -> Workout:
    workout.name = data.name
    workout.week = data.week
    workout.day_of_week = data.day_of_week
    workout.kind = data.kind
    workout.position = data.position
    workout.notes = data.notes
    # delete-orphan cascade removes the previous block tree.
    workout.blocks = _build_blocks(data.blocks)
    db.commit()
    return get_workout(db, workout.id)


def delete_workout(db: Session, workout: Workout) -> None:
    db.delete(workout)
    db.commit()
