import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import { api } from "./client";
import type { WorkoutCreate, WorkoutReplace } from "./types";

// --- Muscle groups ---
export const useMuscleGroups = () =>
  useQuery({ queryKey: ["muscle-groups"], queryFn: api.muscleGroups.list });

export function useMuscleGroupMutations() {
  const qc = useQueryClient();
  const invalidate = () => qc.invalidateQueries({ queryKey: ["muscle-groups"] });
  return {
    create: useMutation({ mutationFn: api.muscleGroups.create, onSuccess: invalidate }),
    update: useMutation({
      mutationFn: (v: { id: number; name?: string; position?: number }) =>
        api.muscleGroups.update(v.id, v),
      onSuccess: invalidate,
    }),
    remove: useMutation({ mutationFn: api.muscleGroups.remove, onSuccess: invalidate }),
  };
}

// --- Exercises ---
export const useExercises = (params?: { muscle_group_id?: number; q?: string }) =>
  useQuery({
    queryKey: ["exercises", params ?? {}],
    queryFn: () => api.exercises.list(params),
  });

export function useExerciseMutations() {
  const qc = useQueryClient();
  const invalidate = () => qc.invalidateQueries({ queryKey: ["exercises"] });
  return {
    create: useMutation({ mutationFn: api.exercises.create, onSuccess: invalidate }),
    update: useMutation({
      mutationFn: (v: { id: number } & Parameters<typeof api.exercises.update>[1]) =>
        api.exercises.update(v.id, v),
      onSuccess: invalidate,
    }),
    remove: useMutation({ mutationFn: api.exercises.remove, onSuccess: invalidate }),
  };
}

// --- Athletes ---
export const useAthletes = () =>
  useQuery({ queryKey: ["athletes"], queryFn: api.athletes.list });

export function useAthleteMutations() {
  const qc = useQueryClient();
  const invalidate = () => qc.invalidateQueries({ queryKey: ["athletes"] });
  return {
    create: useMutation({ mutationFn: api.athletes.create, onSuccess: invalidate }),
    update: useMutation({
      mutationFn: (v: { id: number; name?: string; note?: string | null }) =>
        api.athletes.update(v.id, v),
      onSuccess: invalidate,
    }),
    remove: useMutation({ mutationFn: api.athletes.remove, onSuccess: invalidate }),
  };
}

// --- Workouts ---
export const useAthleteWorkouts = (athleteId: number | null) =>
  useQuery({
    queryKey: ["workouts", athleteId],
    queryFn: () => api.athletes.workouts(athleteId!),
    enabled: athleteId != null,
  });

export const useWorkout = (workoutId: number | null) =>
  useQuery({
    queryKey: ["workout", workoutId],
    queryFn: () => api.workouts.get(workoutId!),
    enabled: workoutId != null,
  });

export function useWorkoutMutations(athleteId: number | null) {
  const qc = useQueryClient();
  const invalidate = () => {
    qc.invalidateQueries({ queryKey: ["workouts", athleteId] });
    qc.invalidateQueries({ queryKey: ["workout"] });
  };
  return {
    create: useMutation({
      mutationFn: (d: WorkoutCreate) => api.workouts.create(d),
      onSuccess: invalidate,
    }),
    replace: useMutation({
      mutationFn: (v: { id: number; data: WorkoutReplace }) =>
        api.workouts.replace(v.id, v.data),
      onSuccess: invalidate,
    }),
    remove: useMutation({ mutationFn: api.workouts.remove, onSuccess: invalidate }),
  };
}
