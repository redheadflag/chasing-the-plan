from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.api.routers import athletes, exercises, muscle_groups, reports, workouts
from app.config import settings

app = FastAPI(
    title="Chasing the Plan",
    description="Generate athlete training plans as .pdf/.xlsx.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Translate DB constraint violations into a clean 409 response."""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Database constraint violation", "error": str(exc.orig)},
    )


@app.get("/api/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(muscle_groups.router)
app.include_router(exercises.router)
app.include_router(athletes.router)
app.include_router(workouts.router)
app.include_router(reports.router)
