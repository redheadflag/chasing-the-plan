from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Athlete
from app.schemas.athlete import AthleteCreate, AthleteUpdate


def list_athletes(db: Session) -> list[Athlete]:
    return list(db.scalars(select(Athlete).order_by(Athlete.name)))


def get_athlete(db: Session, athlete_id: int) -> Athlete | None:
    return db.get(Athlete, athlete_id)


def create_athlete(db: Session, data: AthleteCreate) -> Athlete:
    athlete = Athlete(name=data.name, note=data.note)
    db.add(athlete)
    db.commit()
    db.refresh(athlete)
    return athlete


def update_athlete(db: Session, athlete: Athlete, data: AthleteUpdate) -> Athlete:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(athlete, field, value)
    db.commit()
    db.refresh(athlete)
    return athlete


def delete_athlete(db: Session, athlete: Athlete) -> None:
    db.delete(athlete)
    db.commit()
