from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_or_404
from app.crud import exercises as crud
from app.database import get_db
from app.schemas.exercise import (
    ExerciseBulkCreate,
    ExerciseBulkResult,
    ExerciseCreate,
    ExerciseOut,
    ExerciseUpdate,
)

router = APIRouter(prefix="/api/exercises", tags=["exercises"])


@router.get("", response_model=list[ExerciseOut])
def list_exercises(
    muscle_group_id: int | None = None,
    q: str | None = Query(default=None, description="case-insensitive name search"),
    include_archived: bool = False,
    db: Session = Depends(get_db),
):
    return crud.list_exercises(db, muscle_group_id, q, include_archived)


@router.post("", response_model=ExerciseOut, status_code=status.HTTP_201_CREATED)
def create_exercise(data: ExerciseCreate, db: Session = Depends(get_db)):
    return crud.create_exercise(db, data)


@router.post(
    "/bulk", response_model=ExerciseBulkResult, status_code=status.HTTP_201_CREATED
)
def bulk_create_exercises(data: ExerciseBulkCreate, db: Session = Depends(get_db)):
    return crud.bulk_create_exercises(db, data)


@router.get("/{exercise_id}", response_model=ExerciseOut)
def get_exercise(exercise_id: int, db: Session = Depends(get_db)):
    return get_or_404(crud.get_exercise(db, exercise_id), "Exercise")


@router.patch("/{exercise_id}", response_model=ExerciseOut)
def update_exercise(
    exercise_id: int, data: ExerciseUpdate, db: Session = Depends(get_db)
):
    exercise = get_or_404(crud.get_exercise(db, exercise_id), "Exercise")
    return crud.update_exercise(db, exercise, data)


@router.delete("/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise(exercise_id: int, db: Session = Depends(get_db)):
    exercise = get_or_404(crud.get_exercise(db, exercise_id), "Exercise")
    crud.delete_exercise(db, exercise)
