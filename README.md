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
Optional filters (combinable): `?week=2` for a single week, `?days=WED&days=FRI` for
specific days, or `?workout_id=…` for one day. The **Plan builder** page groups days by
week and has **Download PDF / XLSX** buttons for the whole plan, per week, and per day.

Each workout (training day) carries a `week` number (default `1`); a plan is just its
days spread across weeks. A whole-plan export spanning more than one week is split with
«Неделя N» section headers, while a single-week or single-day export stays flat.

## Tests

```bash
docker compose up -d postgres      # tests use a chasing_the_plan_test database
uv run pytest
```

Covers CRUD, bulk-import idempotency, nested workout create/replace, validation rules,
and that both report formats download with the right content and hyperlinks.

## Deployment (self-hosted)

**Backend + database run in Docker; the frontend is served by your own host nginx (with TLS).**
Postgres uses a persistent `pgdata` volume, and the backend applies migrations automatically on
startup (`docker-entrypoint.sh` → `alembic upgrade head`), with the Cyrillic PDF font bundled in
the image. The backend is published on `127.0.0.1` only, so nginx proxies to it while it stays
off the public internet.

**1. Backend + Postgres:**
```bash
cp .env.prod.example .env.prod          # set POSTGRES_PASSWORD (and BACKEND_PORT if not 8000)
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build
```
The API is now on `127.0.0.1:8000`.

**2. Frontend (built once, served by nginx):**
```bash
cd frontend && npm ci && npm run build   # -> frontend/dist
sudo cp -r dist/* /var/www/chasing-the-plan/
```
The SPA calls a relative `/api`, so it needs no per-domain rebuild.

**3. nginx (HTTP first):** base your site on [`deploy/nginx.example.conf`](deploy/nginx.example.conf)
(HTTP-only; serves `dist/` and proxies `/api` → `127.0.0.1:8000`). Set `server_name`/`root`,
symlink it into `sites-enabled`, then `sudo nginx -t && sudo systemctl reload nginx`.

**4. HTTPS later:** `sudo certbot --nginx -d your.domain` — certbot edits the block to add the
TLS server and the HTTP→HTTPS redirect automatically.

Since nginx serves the SPA and proxies `/api` under one domain, it's **same-origin — no CORS**.

**Operations:**
- **Seed** the catalog once (optional): `sed -n '/^{/,$p' seed/exercises.http | curl -s -X POST https://your.domain/api/exercises/bulk -H 'Content-Type: application/json' -d @-`
- **Updates** — `git pull && docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build` (migrations re-run); rebuild the frontend and recopy `dist/`.
- **Backups** — `docker exec <postgres-container> pg_dump -U ctp chasing_the_plan > backup.sql`.

Files: `Dockerfile` + `docker-entrypoint.sh` (backend), `docker-compose.prod.yml`,
`.env.prod.example`, `deploy/nginx.example.conf`.

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
