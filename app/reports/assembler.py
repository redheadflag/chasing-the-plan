from __future__ import annotations

from dataclasses import dataclass, field

from app.models import Athlete, PlanExercise, Workout
from app.models.enums import BlockType, PlanExerciseKind
from app.reports.format import day_name, format_weight, sets_label


@dataclass
class StageCell:
    """One set-stage column, e.g. top='8кг х 5', bottom='2 серии'."""

    top: str
    bottom: str


@dataclass
class PlanRow:
    muscle_group: str
    exercise_name: str
    exercise_url: str | None
    stages: list[StageCell]
    note: str | None
    highlight: bool
    # A "band" is one block: a SINGLE unit, or all units of a SUPERSET grouped
    # together (consecutive rows, no separator between them).
    band_id: int
    is_superset: bool
    block_note: str | None


@dataclass
class DaySection:
    title: str
    rows: list[PlanRow]
    notes: str | None
    week: int = 1


@dataclass
class PlanDoc:
    athlete_name: str
    athlete_note: str | None
    days: list[DaySection] = field(default_factory=list)
    max_stages: int = 1
    # True when the document spans more than one week, so renderers add
    # "Неделя N" separators. A single-week (or single-day) export stays flat.
    multi_week: bool = False


def _stage_cell(entry: PlanExercise) -> StageCell:
    if entry.kind is PlanExerciseKind.TIME:
        top = f"{entry.duration_seconds}сек"
    elif entry.weight is None:
        top = f"{entry.reps}раз"
    else:
        top = f"{format_weight(entry.weight)}кг х {entry.reps}"
    return StageCell(top=top, bottom=sets_label(entry.sets))


def build_plan_doc(athlete: Athlete, workouts: list[Workout]) -> PlanDoc:
    """Turn ORM objects into a renderer-agnostic document used by both renderers."""
    doc = PlanDoc(athlete_name=athlete.name, athlete_note=athlete.note)
    max_stages = 1

    for workout in workouts:
        rows: list[PlanRow] = []
        for block in workout.blocks:
            is_superset = block.block_type is BlockType.SUPERSET
            for unit in block.units:
                stages = [_stage_cell(e) for e in unit.entries]
                max_stages = max(max_stages, len(stages))
                rows.append(
                    PlanRow(
                        muscle_group=unit.exercise.muscle_group.name,
                        exercise_name=unit.exercise.name,
                        exercise_url=unit.exercise.url,
                        stages=stages,
                        note=unit.note,
                        highlight=unit.highlight,
                        band_id=block.id,
                        is_superset=is_superset,
                        block_note=block.note,
                    )
                )
        doc.days.append(
            DaySection(
                title=f"{day_name(workout.day_of_week)} ({workout.name})",
                rows=rows,
                notes=workout.notes,
                week=workout.week,
            )
        )

    doc.max_stages = max_stages
    doc.multi_week = len({w.week for w in workouts}) > 1
    return doc
