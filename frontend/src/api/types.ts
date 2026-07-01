export type DayOfWeek = "MON" | "TUE" | "WED" | "THU" | "FRI" | "SAT" | "SUN";
export type WorkoutKind = "ORDINARY" | "SUPERSET_BASED";
export type BlockType = "SINGLE" | "SUPERSET";
export type PlanExerciseKind = "WEIGHT" | "TIME";

export const DAY_LABELS: Record<DayOfWeek, string> = {
  MON: "Понедельник",
  TUE: "Вторник",
  WED: "Среда",
  THU: "Четверг",
  FRI: "Пятница",
  SAT: "Суббота",
  SUN: "Воскресенье",
};
export const DAYS: DayOfWeek[] = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"];

export interface MuscleGroup {
  id: number;
  name: string;
  position: number;
}

export interface Exercise {
  id: number;
  name: string;
  url: string | null;
  muscle_group_id: number;
  archived: boolean;
  muscle_group?: MuscleGroup | null;
}

export interface Athlete {
  id: number;
  name: string;
  note: string | null;
}

export interface WorkoutSummary {
  id: number;
  athlete_id: number;
  name: string;
  day_of_week: DayOfWeek;
  kind: WorkoutKind;
  position: number;
}

// --- workout write payloads ---
export interface PlanExerciseIn {
  kind: PlanExerciseKind;
  sets: number;
  reps?: number | null;
  weight?: number | null;
  duration_seconds?: number | null;
}
export interface PlanUnitIn {
  exercise_id: number;
  note?: string | null;
  highlight: boolean;
  entries: PlanExerciseIn[];
}
export interface WorkoutBlockIn {
  block_type: BlockType;
  note?: string | null;
  units: PlanUnitIn[];
}
export interface WorkoutCreate {
  athlete_id: number;
  name: string;
  day_of_week: DayOfWeek;
  kind: WorkoutKind;
  position: number;
  notes?: string | null;
  blocks: WorkoutBlockIn[];
}
export type WorkoutReplace = Omit<WorkoutCreate, "athlete_id">;

// --- workout read payloads ---
export interface PlanExerciseOut {
  id: number;
  position: number;
  kind: PlanExerciseKind;
  sets: number;
  reps: number | null;
  weight: string | number | null;
  duration_seconds: number | null;
}
export interface PlanUnitOut {
  id: number;
  position: number;
  exercise_id: number;
  note: string | null;
  highlight: boolean;
  exercise: Exercise;
  entries: PlanExerciseOut[];
}
export interface WorkoutBlockOut {
  id: number;
  position: number;
  block_type: BlockType;
  note: string | null;
  units: PlanUnitOut[];
}
export interface WorkoutOut {
  id: number;
  athlete_id: number;
  name: string;
  day_of_week: DayOfWeek;
  kind: WorkoutKind;
  position: number;
  notes: string | null;
  blocks: WorkoutBlockOut[];
}
