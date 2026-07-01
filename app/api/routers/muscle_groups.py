from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_or_404
from app.crud import muscle_groups as crud
from app.database import get_db
from app.schemas.muscle_group import (
    MuscleGroupCreate,
    MuscleGroupOut,
    MuscleGroupUpdate,
)

router = APIRouter(prefix="/api/muscle-groups", tags=["muscle-groups"])


@router.get("", response_model=list[MuscleGroupOut])
def list_muscle_groups(db: Session = Depends(get_db)):
    return crud.list_muscle_groups(db)


@router.post("", response_model=MuscleGroupOut, status_code=status.HTTP_201_CREATED)
def create_muscle_group(data: MuscleGroupCreate, db: Session = Depends(get_db)):
    return crud.create_muscle_group(db, data)


@router.patch("/{group_id}", response_model=MuscleGroupOut)
def update_muscle_group(
    group_id: int, data: MuscleGroupUpdate, db: Session = Depends(get_db)
):
    group = get_or_404(crud.get_muscle_group(db, group_id), "Muscle group")
    return crud.update_muscle_group(db, group, data)


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_muscle_group(group_id: int, db: Session = Depends(get_db)):
    group = get_or_404(crud.get_muscle_group(db, group_id), "Muscle group")
    crud.delete_muscle_group(db, group)
