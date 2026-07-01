import type {
  Athlete,
  Exercise,
  MuscleGroup,
  WorkoutCreate,
  WorkoutOut,
  WorkoutReplace,
  WorkoutSummary,
} from "./types";

const BASE = (import.meta.env.VITE_API_BASE as string | undefined) ?? "";

async function req<T>(path: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}/api${path}`, {
    headers: { "Content-Type": "application/json", ...(opts?.headers ?? {}) },
    ...opts,
  });
  if (!res.ok) {
    let detail: unknown = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      /* ignore */
    }
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const reportUrl = (
  athleteId: number,
  ext: "pdf" | "xlsx",
  opts?: { workoutId?: number; days?: string[] },
) => {
  const params = new URLSearchParams();
  if (opts?.workoutId != null) params.set("workout_id", String(opts.workoutId));
  (opts?.days ?? []).forEach((d) => params.append("days", d));
  const qs = params.toString();
  return `${BASE}/api/athletes/${athleteId}/plan.${ext}${qs ? `?${qs}` : ""}`;
};

export const api = {
  muscleGroups: {
    list: () => req<MuscleGroup[]>("/muscle-groups"),
    create: (d: { name: string; position?: number }) =>
      req<MuscleGroup>("/muscle-groups", { method: "POST", body: JSON.stringify(d) }),
    update: (id: number, d: Partial<{ name: string; position: number }>) =>
      req<MuscleGroup>(`/muscle-groups/${id}`, {
        method: "PATCH",
        body: JSON.stringify(d),
      }),
    remove: (id: number) => req<void>(`/muscle-groups/${id}`, { method: "DELETE" }),
  },
  exercises: {
    list: (params?: { muscle_group_id?: number; q?: string }) => {
      const qs = new URLSearchParams();
      if (params?.muscle_group_id) qs.set("muscle_group_id", String(params.muscle_group_id));
      if (params?.q) qs.set("q", params.q);
      const suffix = qs.toString() ? `?${qs}` : "";
      return req<Exercise[]>(`/exercises${suffix}`);
    },
    create: (d: { name: string; url: string | null; muscle_group_id: number }) =>
      req<Exercise>("/exercises", { method: "POST", body: JSON.stringify(d) }),
    update: (
      id: number,
      d: Partial<{ name: string; url: string | null; muscle_group_id: number; archived: boolean }>,
    ) => req<Exercise>(`/exercises/${id}`, { method: "PATCH", body: JSON.stringify(d) }),
    remove: (id: number) => req<void>(`/exercises/${id}`, { method: "DELETE" }),
  },
  athletes: {
    list: () => req<Athlete[]>("/athletes"),
    create: (d: { name: string; note: string | null }) =>
      req<Athlete>("/athletes", { method: "POST", body: JSON.stringify(d) }),
    update: (id: number, d: Partial<{ name: string; note: string | null }>) =>
      req<Athlete>(`/athletes/${id}`, { method: "PATCH", body: JSON.stringify(d) }),
    remove: (id: number) => req<void>(`/athletes/${id}`, { method: "DELETE" }),
    workouts: (id: number) => req<WorkoutSummary[]>(`/athletes/${id}/workouts`),
  },
  workouts: {
    get: (id: number) => req<WorkoutOut>(`/workouts/${id}`),
    create: (d: WorkoutCreate) =>
      req<WorkoutOut>("/workouts", { method: "POST", body: JSON.stringify(d) }),
    replace: (id: number, d: WorkoutReplace) =>
      req<WorkoutOut>(`/workouts/${id}`, { method: "PUT", body: JSON.stringify(d) }),
    remove: (id: number) => req<void>(`/workouts/${id}`, { method: "DELETE" }),
  },
};
