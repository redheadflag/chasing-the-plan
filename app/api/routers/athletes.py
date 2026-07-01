from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_or_404
from app.crud import athletes as crud
from app.crud import workouts as workouts_crud
from app.database import get_db
from app.schemas.athlete import AthleteCreate, AthleteOut, AthleteUpdate
from app.schemas.workout import WorkoutSummary

router = APIRouter(prefix="/api/athletes", tags=["athletes"])


@router.get("", response_model=list[AthleteOut])
def list_athletes(db: Session = Depends(get_db)):
    return crud.list_athletes(db)


@router.post("", response_model=AthleteOut, status_code=status.HTTP_201_CREATED)
def create_athlete(data: AthleteCreate, db: Session = Depends(get_db)):
    return crud.create_athlete(db, data)


@router.get("/{athlete_id}", response_model=AthleteOut)
def get_athlete(athlete_id: int, db: Session = Depends(get_db)):
    return get_or_404(crud.get_athlete(db, athlete_id), "Athlete")


@router.patch("/{athlete_id}", response_model=AthleteOut)
def update_athlete(
    athlete_id: int, data: AthleteUpdate, db: Session = Depends(get_db)
):
    athlete = get_or_404(crud.get_athlete(db, athlete_id), "Athlete")
    return crud.update_athlete(db, athlete, data)


@router.delete("/{athlete_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_athlete(athlete_id: int, db: Session = Depends(get_db)):
    athlete = get_or_404(crud.get_athlete(db, athlete_id), "Athlete")
    crud.delete_athlete(db, athlete)


@router.get("/{athlete_id}/workouts", response_model=list[WorkoutSummary])
def list_athlete_workouts(athlete_id: int, db: Session = Depends(get_db)):
    get_or_404(crud.get_athlete(db, athlete_id), "Athlete")
    return workouts_crud.list_workouts_for_athlete(db, athlete_id)
