from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_or_404
from app.crud import athletes as athletes_crud
from app.crud import workouts as crud
from app.database import get_db
from app.schemas.workout import WorkoutCreate, WorkoutOut, WorkoutReplace

router = APIRouter(prefix="/api/workouts", tags=["workouts"])


@router.post("", response_model=WorkoutOut, status_code=status.HTTP_201_CREATED)
def create_workout(data: WorkoutCreate, db: Session = Depends(get_db)):
    get_or_404(athletes_crud.get_athlete(db, data.athlete_id), "Athlete")
    return crud.create_workout(db, data)


@router.get("/{workout_id}", response_model=WorkoutOut)
def get_workout(workout_id: int, db: Session = Depends(get_db)):
    return get_or_404(crud.get_workout(db, workout_id), "Workout")


@router.put("/{workout_id}", response_model=WorkoutOut)
def replace_workout(
    workout_id: int, data: WorkoutReplace, db: Session = Depends(get_db)
):
    workout = get_or_404(crud.get_workout(db, workout_id), "Workout")
    return crud.replace_workout(db, workout, data)


@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(workout_id: int, db: Session = Depends(get_db)):
    workout = get_or_404(crud.get_workout(db, workout_id), "Workout")
    crud.delete_workout(db, workout)
