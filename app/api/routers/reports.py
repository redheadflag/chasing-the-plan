from __future__ import annotations

from urllib.parse import quote

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.api.deps import get_or_404
from app.crud import athletes as athletes_crud
from app.crud import workouts as workouts_crud
from app.database import get_db
from app.models import Workout
from app.models.enums import DayOfWeek
from app.reports.assembler import build_plan_doc
from app.reports.format import day_name
from app.reports.pdf import render_pdf
from app.reports.xlsx import render_xlsx

router = APIRouter(prefix="/api/athletes", tags=["reports"])

XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
PDF_MIME = "application/pdf"


def _content_disposition(filename: str) -> str:
    """attachment with both ascii fallback and UTF-8 (RFC 5987) filename."""
    ascii_name = filename.encode("ascii", "ignore").decode().strip() or "plan"
    return f"attachment; filename=\"{ascii_name}\"; filename*=UTF-8''{quote(filename)}"


def _load(
    db: Session,
    athlete_id: int,
    days: list[DayOfWeek] | None,
    workout_id: int | None,
    week: int | None,
) -> tuple[object, list[Workout]]:
    athlete = get_or_404(athletes_crud.get_athlete(db, athlete_id), "Athlete")
    workouts = workouts_crud.get_athlete_plan(db, athlete_id)
    if workout_id is not None:
        workouts = [w for w in workouts if w.id == workout_id]
    else:
        if week is not None:
            workouts = [w for w in workouts if w.week == week]
        if days:
            wanted = set(days)
            workouts = [w for w in workouts if w.day_of_week in wanted]
    return build_plan_doc(athlete, workouts), workouts


def _filename(workouts: list[Workout], ext: str, week: int | None = None) -> str:
    """Filename without the athlete's name.

    An explicit per-week download is named after the week; a single-workout
    download (the per-day button) is named after its day; otherwise it's the
    generic whole-plan title.
    """
    if week is not None:
        return f"Неделя {week}.{ext}"
    if len(workouts) == 1:
        w = workouts[0]
        return f"{day_name(w.day_of_week)} - {w.name}.{ext}"
    return f"План тренировок.{ext}"


@router.get("/{athlete_id}/plan.xlsx")
def download_plan_xlsx(
    athlete_id: int,
    days: list[DayOfWeek] | None = Query(default=None),
    workout_id: int | None = Query(default=None),
    week: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
):
    doc, workouts = _load(db, athlete_id, days, workout_id, week)
    content = render_xlsx(doc)
    return Response(
        content=content,
        media_type=XLSX_MIME,
        headers={"Content-Disposition": _content_disposition(_filename(workouts, "xlsx", week))},
    )


@router.get("/{athlete_id}/plan.pdf")
def download_plan_pdf(
    athlete_id: int,
    days: list[DayOfWeek] | None = Query(default=None),
    workout_id: int | None = Query(default=None),
    week: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
):
    doc, workouts = _load(db, athlete_id, days, workout_id, week)
    content = render_pdf(doc)
    return Response(
        content=content,
        media_type=PDF_MIME,
        headers={"Content-Disposition": _content_disposition(_filename(workouts, "pdf", week))},
    )
