# Chasing the Plan

A service for building athlete **training plans** and exporting them as **`.pdf`** and
**`.xlsx`** files (downloaded straight to the browser), closely matching the samples in
[`samples/`](samples/).

- **Backend:** FastAPI · SQLAlchemy 2.0 ORM · Alembic · PostgreSQL
- **Frontend:** React + TypeScript (Vite) · TanStack Query · Tailwind CSS
- **Reports:** `openpyxl` (xlsx) and `reportlab` (pdf), with Cyrillic support and
  hyperlinked exercise names.

---

## Features

- **Exercises UI** — manage muscle groups and exercises (name, muscle group, URL link).
- **Athletes UI** — manage athletes (name, note).
- **Plan builder** — per athlete, build day-by-day workouts as **ordinary** or
  **superset-based**; each exercise placement holds an ordered list of set-stages
  (weight `sets × reps @ kg` or time `sets × seconds`). Mark exercises "film this".
- **Report generation** — download a `.pdf` / `.xlsx` per athlete. Layout mirrors the
  sample: day headers, muscle-group column, per-stage columns, superset grouping,
  green "film this" highlight, per-workout notes, and hyperlinked exercise names.
- **Bulk seed** — [`seed/exercises.http`](seed/exercises.http) populates the catalog from
  the sample workbook through a real endpoint.

## Data model

One `workout` (athlete + day + name + kind) is composed of ordered **blocks**; each block
is either a `SINGLE` exercise or a `SUPERSET` of several. A block holds **plan units**
(one exercise each) and each unit holds ordered **plan exercises** (the set-stages).

```
athlete ─< workout ─< workout_block ─< plan_unit ─< plan_exercise
                                          │
exercise >──────────────────────────────┘   (RESTRICT)
muscle_group ─< exercise
```

Notable choices beyond the raw entity list (see the plan for rationale):
`workout` + `workout_block` unify "ordinary" and "superset-based" workouts (a real day
mixes both); the `exercise` FK lives on `plan_unit`; `plan_exercise` is a single
discriminated table (`WEIGHT`/`TIME`); every ordered relation has a `position`;
`plan_unit.highlight` drives the green marker; unique constraints + `archived` + a
`RESTRICT` FK protect historical plans.

---

## Prerequisites

- Python **3.13** and [`uv`](https://docs.astral.sh/uv/)
- Node **20+** and npm
- Docker (for PostgreSQL)

## Backend

```bash
# 1. Start PostgreSQL
docker compose up -d postgres

# 2. Configure env (defaults already point at the docker DB)
cp .env.example .env

# 3. Install deps + apply migrations
uv sync --extra dev
uv run alembic upgrade head

# 4. Run the API (docs at http://localhost:8000/docs)
uv run uvicorn app.main:app --reload
```

### Seed the exercise catalog

With the API running, replay the generated requests (VS Code **REST Client**, JetBrains
`.http`, or convert to curl):

```bash
# regenerate from the sample workbook (optional)
uv run python seed/generate_seed_http.py
# then POST seed/exercises.http  ->  POST /api/exercises/bulk  (idempotent)
```

## Frontend

```bash
cd frontend
npm install
npm run dev          # http://localhost:5173  (proxies /api -> :8000)
```

Build for production with `npm run build` (output in `frontend/dist/`).

## Reports

- `GET /api/athletes/{id}/plan.pdf`
- `GET /api/athletes/{id}/plan.xlsx`

Both return an attachment (`Content-Disposition`) so the browser downloads the file.
Optional `?days=WED&days=FRI` filters to specific days. The **Plan builder** page has
**Download PDF / XLSX** buttons wired to these.

## Tests

```bash
docker compose up -d postgres      # tests use a chasing_the_plan_test database
uv run pytest
```

Covers CRUD, bulk-import idempotency, nested workout create/replace, validation rules,
and that both report formats download with the right content and hyperlinks.

## Project structure

```
app/
  api/routers/     # muscle_groups, exercises, athletes, workouts, reports
  crud/            # query/mutation helpers per aggregate
  models/          # SQLAlchemy models + enums
  schemas/         # Pydantic v2 (nested workout create/read)
  reports/         # assembler (shared) + xlsx + pdf renderers + DejaVu fonts
  config.py  database.py  main.py
alembic/           # migrations
frontend/          # React + TS app (Vite)
seed/              # xlsx -> exercises.http generator + output
tests/             # pytest (in-process TestClient)
docker-compose.yml # postgres + adminer
```
