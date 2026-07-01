from __future__ import annotations

from typing import TypeVar

from fastapi import HTTPException, status

T = TypeVar("T")


def get_or_404(obj: T | None, name: str = "Resource") -> T:
    if obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{name} not found"
        )
    return obj
