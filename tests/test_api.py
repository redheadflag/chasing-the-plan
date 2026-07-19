from __future__ import annotations

from fastapi.testclient import TestClient


def test_health(client: TestClient):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_muscle_group_crud(client: TestClient):
    r = client.post("/api/muscle-groups", json={"name": "СПИНА"})
    assert r.status_code == 201
    gid = r.json()["id"]

    assert any(g["name"] == "СПИНА" for g in client.get("/api/muscle-groups").json())

    client.patch(f"/api/muscle-groups/{gid}", json={"name": "СПИНА/ШИРОЧАЙШИЕ"})
    assert client.get("/api/muscle-groups").json()[0]["name"] == "СПИНА/ШИРОЧАЙШИЕ"

    assert client.delete(f"/api/muscle-groups/{gid}").status_code == 204
    assert client.get("/api/muscle-groups").json() == []


def test_duplicate_muscle_group_conflicts(client: TestClient):
    client.post("/api/muscle-groups", json={"name": "СПИНА"}).raise_for_status()
    r = client.post("/api/muscle-groups", json={"name": "СПИНА"})
    assert r.status_code == 409


def test_exercise_crud_and_filter(client: TestClient):
    gid = client.post("/api/muscle-groups", json={"name": "ГРУДЬ"}).json()["id"]
    r = client.post(
        "/api/exercises",
        json={"name": "BENCH PRESS", "url": "https://x", "muscle_group_id": gid},
    )
    assert r.status_code == 201
    ex = r.json()
    assert ex["muscle_group"]["name"] == "ГРУДЬ"

    # filter by group and search
    assert len(client.get(f"/api/exercises?muscle_group_id={gid}").json()) == 1
    assert len(client.get("/api/exercises?q=bench").json()) == 1
    assert len(client.get("/api/exercises?q=zzz").json()) == 0

    client.patch(f"/api/exercises/{ex['id']}", json={"name": "PAUSED BENCH PRESS"})
    assert client.get(f"/api/exercises/{ex['id']}").json()["name"] == "PAUSED BENCH PRESS"


def test_bulk_import_is_idempotent(client: TestClient, sample_catalog):
    # sample_catalog already imported 3 exercises + 2 groups
    assert len(client.get("/api/exercises").json()) == 3
    # re-import the same data -> everything skipped
    body = {
        "create_missing_groups": True,
        "items": [{"muscle_group": "CROSSFIT", "name": "TURKISH GETUP", "url": None}],
    }
    result = client.post("/api/exercises/bulk", json=body).json()
    assert result["created_exercises"] == 0
    assert result["skipped_existing"] == 1


def test_bulk_backfills_missing_urls(client: TestClient):
    gid = client.post("/api/muscle-groups", json={"name": "СПИНА"}).json()["id"]
    ex = client.post(
        "/api/exercises", json={"name": "LAT PULLDOWN", "url": None, "muscle_group_id": gid}
    ).json()
    assert ex["url"] is None

    body = {
        "create_missing_groups": True,
        "items": [{"muscle_group": "СПИНА", "name": "LAT PULLDOWN", "url": "https://ex/lp"}],
    }
    result = client.post("/api/exercises/bulk", json=body).json()
    assert result["updated_urls"] == 1
    assert result["created_exercises"] == 0
    assert client.get(f"/api/exercises/{ex['id']}").json()["url"] == "https://ex/lp"


def test_athlete_crud(client: TestClient):
    a = client.post("/api/athletes", json={"name": "Иван", "note": "заметка"}).json()
    assert a["name"] == "Иван"
    client.patch(f"/api/athletes/{a['id']}", json={"note": None})
    assert client.get(f"/api/athletes/{a['id']}").json()["note"] is None
    assert client.delete(f"/api/athletes/{a['id']}").status_code == 204


def _workout_payload(athlete_id: int, cat: dict[str, int]) -> dict:
    return {
        "athlete_id": athlete_id,
        "name": "Crossfit",
        "day_of_week": "WED",
        "kind": "ORDINARY",
        "notes": "note block",
        "blocks": [
            {
                "block_type": "SINGLE",
                "units": [
                    {
                        "exercise_id": cat["TURKISH GETUP"],
                        "note": "5 per arm",
                        "highlight": True,
                        "entries": [
                            {"kind": "WEIGHT", "sets": 1, "reps": 5, "weight": 4},
                            {"kind": "WEIGHT", "sets": 2, "reps": 5, "weight": 8},
                        ],
                    }
                ],
            },
            {
                "block_type": "SUPERSET",
                "note": "Делаешь суперсетом.",
                "units": [
                    {
                        "exercise_id": cat["TRX LOW ROW"],
                        "highlight": False,
                        "entries": [{"kind": "WEIGHT", "sets": 3, "reps": 10, "weight": None}],
                    },
                    {
                        "exercise_id": cat["FLUTTER KICK"],
                        "highlight": False,
                        "entries": [{"kind": "TIME", "sets": 3, "duration_seconds": 20}],
                    },
                ],
            },
        ],
    }


def test_workout_nested_create_get_replace_delete(client: TestClient, sample_catalog):
    a = client.post("/api/athletes", json={"name": "Иван", "note": None}).json()
    payload = _workout_payload(a["id"], sample_catalog)

    r = client.post("/api/workouts", json=payload)
    assert r.status_code == 201
    w = r.json()
    assert len(w["blocks"]) == 2
    assert w["blocks"][0]["units"][0]["highlight"] is True
    assert len(w["blocks"][0]["units"][0]["entries"]) == 2
    assert w["blocks"][1]["block_type"] == "SUPERSET"
    # bodyweight entry -> weight null
    assert w["blocks"][1]["units"][0]["entries"][0]["weight"] is None
    # time entry
    assert w["blocks"][1]["units"][1]["entries"][0]["duration_seconds"] == 20

    # listed under athlete
    workouts = client.get(f"/api/athletes/{a['id']}/workouts").json()
    assert len(workouts) == 1

    # replace: drop to a single block
    replace = {k: v for k, v in payload.items() if k != "athlete_id"}
    replace["blocks"] = [payload["blocks"][0]]
    r2 = client.put(f"/api/workouts/{w['id']}", json=replace)
    assert r2.status_code == 200
    assert len(r2.json()["blocks"]) == 1

    assert client.delete(f"/api/workouts/{w['id']}").status_code == 204
    assert client.get(f"/api/workouts/{w['id']}").status_code == 404


def test_workout_week_roundtrip_and_ordering(client: TestClient, sample_catalog):
    a = client.post("/api/athletes", json={"name": "Иван", "note": None}).json()

    # week is persisted on create, get, and summary
    payload = _workout_payload(a["id"], sample_catalog)
    payload["week"] = 3
    w = client.post("/api/workouts", json=payload).json()
    assert w["week"] == 3
    assert client.get(f"/api/workouts/{w['id']}").json()["week"] == 3
    assert client.get(f"/api/athletes/{a['id']}/workouts").json()[0]["week"] == 3

    # replace can move a day to another week
    replace = {k: v for k, v in payload.items() if k != "athlete_id"}
    replace["week"] = 5
    assert client.put(f"/api/workouts/{w['id']}", json=replace).json()["week"] == 5

    # omitting week defaults to 1
    p2 = _workout_payload(a["id"], sample_catalog)
    p2["day_of_week"] = "MON"
    p2.pop("week", None)
    assert client.post("/api/workouts", json=p2).json()["week"] == 1

    # athlete's workouts come back ordered by descending week
    summary = client.get(f"/api/athletes/{a['id']}/workouts").json()
    assert [s["week"] for s in summary] == [5, 1]


def test_single_block_must_have_one_unit(client: TestClient, sample_catalog):
    a = client.post("/api/athletes", json={"name": "A", "note": None}).json()
    bad = {
        "athlete_id": a["id"],
        "name": "x",
        "day_of_week": "MON",
        "kind": "ORDINARY",
        "blocks": [
            {
                "block_type": "SINGLE",
                "units": [
                    {"exercise_id": sample_catalog["TURKISH GETUP"], "highlight": False,
                     "entries": [{"kind": "WEIGHT", "sets": 1, "reps": 5, "weight": 4}]},
                    {"exercise_id": sample_catalog["TRX LOW ROW"], "highlight": False,
                     "entries": [{"kind": "WEIGHT", "sets": 1, "reps": 5, "weight": 4}]},
                ],
            }
        ],
    }
    assert client.post("/api/workouts", json=bad).status_code == 422


def test_weight_entry_requires_reps(client: TestClient, sample_catalog):
    a = client.post("/api/athletes", json={"name": "A", "note": None}).json()
    bad = {
        "athlete_id": a["id"],
        "name": "x",
        "day_of_week": "MON",
        "kind": "ORDINARY",
        "blocks": [
            {
                "block_type": "SINGLE",
                "units": [
                    {"exercise_id": sample_catalog["TURKISH GETUP"], "highlight": False,
                     "entries": [{"kind": "WEIGHT", "sets": 1, "weight": 4}]},
                ],
            }
        ],
    }
    assert client.post("/api/workouts", json=bad).status_code == 422
