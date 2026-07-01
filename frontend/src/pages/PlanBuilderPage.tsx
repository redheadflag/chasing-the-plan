import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { reportUrl } from "../api/client";
import {
  useAthletes,
  useAthleteWorkouts,
  useExercises,
  useMuscleGroups,
  useWorkout,
  useWorkoutMutations,
} from "../api/hooks";
import {
  DAY_LABELS,
  DAYS,
  type BlockType,
  type DayOfWeek,
  type Exercise,
  type MuscleGroup,
  type PlanExerciseKind,
  type WorkoutCreate,
  type WorkoutKind,
  type WorkoutOut,
} from "../api/types";
import { Combobox } from "../components/Combobox";
import { Badge, Button, ErrorBox, Field, Select, Spinner, TextArea, TextInput } from "../components/ui";

// ------- Draft model (editable shape) -------
interface DraftEntry {
  kind: PlanExerciseKind;
  sets: number;
  reps: number | null;
  weight: string; // "" => bodyweight
  duration: number | null;
}
interface DraftUnit {
  exercise_id: number;
  highlight: boolean;
  note: string;
  entries: DraftEntry[];
}
interface DraftBlock {
  block_type: BlockType;
  note: string;
  units: DraftUnit[];
}
interface Draft {
  name: string;
  day_of_week: DayOfWeek;
  kind: WorkoutKind;
  notes: string;
  blocks: DraftBlock[];
}

const newEntry = (): DraftEntry => ({
  kind: "WEIGHT",
  sets: 3,
  reps: 10,
  weight: "",
  duration: null,
});
const newUnit = (): DraftUnit => ({
  exercise_id: 0, // 0 = not chosen yet (pick a muscle group, then an exercise)
  highlight: false,
  note: "",
  entries: [newEntry()],
});

function fromWorkout(w: WorkoutOut): Draft {
  return {
    name: w.name,
    day_of_week: w.day_of_week,
    kind: w.kind,
    notes: w.notes ?? "",
    blocks: w.blocks.map((b) => ({
      block_type: b.block_type,
      note: b.note ?? "",
      units: b.units.map((u) => ({
        exercise_id: u.exercise_id,
        highlight: u.highlight,
        note: u.note ?? "",
        entries: u.entries.map((e) => ({
          kind: e.kind,
          sets: e.sets,
          reps: e.reps,
          weight: e.weight == null ? "" : String(e.weight),
          duration: e.duration_seconds,
        })),
      })),
    })),
  };
}

function toPayload(draft: Draft, athleteId: number): WorkoutCreate {
  return {
    athlete_id: athleteId,
    name: draft.name.trim(),
    day_of_week: draft.day_of_week,
    kind: draft.kind,
    position: 0,
    notes: draft.notes.trim() || null,
    blocks: draft.blocks.map((b) => ({
      block_type: b.block_type,
      note: b.note.trim() || null,
      units: b.units.map((u) => ({
        exercise_id: u.exercise_id,
        highlight: u.highlight,
        note: u.note.trim() || null,
        entries: u.entries.map((e) =>
          e.kind === "WEIGHT"
            ? {
                kind: "WEIGHT" as const,
                sets: e.sets,
                reps: e.reps ?? 1,
                weight: e.weight.trim() === "" ? null : Number(e.weight),
              }
            : {
                kind: "TIME" as const,
                sets: e.sets,
                duration_seconds: e.duration ?? 1,
              },
        ),
      })),
    })),
  };
}

export default function PlanBuilderPage() {
  const athletesQ = useAthletes();
  const [searchParams, setSearchParams] = useSearchParams();
  const athleteParam = searchParams.get("athlete");
  const [athleteId, setAthleteId] = useState<number | null>(
    athleteParam ? Number(athleteParam) : null,
  );

  // Default to first athlete once loaded.
  useEffect(() => {
    if (athleteId == null && athletesQ.data && athletesQ.data.length > 0) {
      setAthleteId(athletesQ.data[0].id);
    }
  }, [athletesQ.data, athleteId]);

  const workoutsQ = useAthleteWorkouts(athleteId);
  const [editing, setEditing] = useState<number | "new" | null>(null);

  return (
    <div>
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-bold">Планы тренировок</h1>
        <div className="flex items-center gap-2">
          <Select
            value={athleteId ?? ""}
            onChange={(e) => {
              const id = e.target.value === "" ? null : Number(e.target.value);
              setAthleteId(id);
              setSearchParams(id ? { athlete: String(id) } : {});
              setEditing(null);
            }}
            className="min-w-48"
          >
            <option value="">— выберите атлета —</option>
            {athletesQ.data?.map((a) => (
              <option key={a.id} value={a.id}>
                {a.name}
              </option>
            ))}
          </Select>
        </div>
      </div>

      {athleteId == null ? (
        <div className="rounded-lg border border-dashed border-slate-300 p-8 text-center text-slate-400">
          Выберите атлета, чтобы работать с его планом.
        </div>
      ) : editing != null ? (
        <WorkoutEditor
          athleteId={athleteId}
          workoutId={editing === "new" ? null : editing}
          onDone={() => setEditing(null)}
        />
      ) : (
        <div>
          <div className="mb-4 flex flex-wrap gap-2">
            <Button onClick={() => setEditing("new")}>+ Тренировка (день)</Button>
            <a href={reportUrl(athleteId, "pdf")}>
              <Button variant="secondary">⬇ Весь план: PDF</Button>
            </a>
            <a href={reportUrl(athleteId, "xlsx")}>
              <Button variant="secondary">⬇ Весь план: XLSX</Button>
            </a>
          </div>

          <ErrorBox error={workoutsQ.error} />
          {workoutsQ.isLoading ? (
            <Spinner />
          ) : (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {workoutsQ.data?.map((w) => (
                <div
                  key={w.id}
                  className="flex flex-col rounded-lg border border-slate-200 bg-white p-4"
                >
                  <button onClick={() => setEditing(w.id)} className="text-left">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold">{DAY_LABELS[w.day_of_week]}</span>
                      <Badge color={w.kind === "SUPERSET_BASED" ? "amber" : "indigo"}>
                        {w.kind === "SUPERSET_BASED" ? "суперсеты" : "обычная"}
                      </Badge>
                    </div>
                    <div className="mt-1 text-slate-600 hover:text-indigo-600">
                      {w.name} <span className="text-xs text-slate-400">— изменить</span>
                    </div>
                  </button>
                  <div className="mt-3 flex gap-2 border-t border-slate-100 pt-3">
                    <a
                      href={reportUrl(athleteId, "pdf", { workoutId: w.id })}
                      className="rounded border border-slate-300 px-2 py-1 text-xs font-medium text-slate-600 hover:bg-slate-50"
                    >
                      ⬇ PDF
                    </a>
                    <a
                      href={reportUrl(athleteId, "xlsx", { workoutId: w.id })}
                      className="rounded border border-slate-300 px-2 py-1 text-xs font-medium text-slate-600 hover:bg-slate-50"
                    >
                      ⬇ XLSX
                    </a>
                  </div>
                </div>
              ))}
              {workoutsQ.data?.length === 0 && (
                <div className="col-span-full rounded-lg border border-dashed border-slate-300 p-8 text-center text-slate-400">
                  Ещё нет тренировок. Добавьте первый день.
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// --------------------- Workout editor ---------------------

function WorkoutEditor({
  athleteId,
  workoutId,
  onDone,
}: {
  athleteId: number;
  workoutId: number | null;
  onDone: () => void;
}) {
  const exercisesQ = useExercises();
  const groupsQ = useMuscleGroups();
  const workoutQ = useWorkout(workoutId);
  const { create, replace, remove } = useWorkoutMutations(athleteId);

  const [draft, setDraft] = useState<Draft | null>(
    workoutId == null
      ? { name: "", day_of_week: "MON", kind: "ORDINARY", notes: "", blocks: [] }
      : null,
  );
  const [validationError, setValidationError] = useState<string | null>(null);

  useEffect(() => {
    if (workoutId != null && workoutQ.data) setDraft(fromWorkout(workoutQ.data));
  }, [workoutId, workoutQ.data]);

  const exercises = exercisesQ.data ?? [];
  const groups = groupsQ.data ?? [];

  if (!draft || exercisesQ.isLoading || groupsQ.isLoading) return <Spinner />;

  const patch = (fn: (d: Draft) => void) =>
    setDraft((prev) => {
      const copy: Draft = structuredClone(prev!);
      fn(copy);
      return copy;
    });

  const setBlockType = (bi: number, type: BlockType) =>
    patch((d) => {
      const block = d.blocks[bi];
      block.block_type = type;
      if (type === "SINGLE" && block.units.length > 1) block.units = [block.units[0]];
    });

  const save = () => {
    const missing = draft.blocks.some((b) => b.units.some((u) => !u.exercise_id));
    if (missing) {
      setValidationError("В каждом упражнении выберите группу мышц и упражнение.");
      return;
    }
    setValidationError(null);
    const payload = toPayload(draft, athleteId);
    if (workoutId == null) create.mutate(payload, { onSuccess: onDone });
    else {
      const { athlete_id, ...rest } = payload;
      void athlete_id;
      replace.mutate({ id: workoutId, data: rest }, { onSuccess: onDone });
    }
  };

  const mutErr = validationError ?? create.error ?? replace.error ?? remove.error;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <button onClick={onDone} className="text-sm text-slate-500 hover:underline">
          ← Назад к списку
        </button>
        <div className="flex gap-2">
          {workoutId != null && (
            <Button
              variant="danger"
              onClick={() => {
                if (confirm("Удалить эту тренировку?"))
                  remove.mutate(workoutId, { onSuccess: onDone });
              }}
            >
              Удалить
            </Button>
          )}
          <Button onClick={save} disabled={create.isPending || replace.isPending}>
            Сохранить
          </Button>
        </div>
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-4">
        <div className="grid gap-4 sm:grid-cols-3">
          <Field label="Название">
            <TextInput
              value={draft.name}
              onChange={(e) => patch((d) => (d.name = e.target.value))}
              placeholder="Напр. Crossfit / Верх"
            />
          </Field>
          <Field label="День недели">
            <Select
              value={draft.day_of_week}
              onChange={(e) => patch((d) => (d.day_of_week = e.target.value as DayOfWeek))}
            >
              {DAYS.map((d) => (
                <option key={d} value={d}>
                  {DAY_LABELS[d]}
                </option>
              ))}
            </Select>
          </Field>
          <Field label="Тип">
            <Select
              value={draft.kind}
              onChange={(e) => patch((d) => (d.kind = e.target.value as WorkoutKind))}
            >
              <option value="ORDINARY">Обычная</option>
              <option value="SUPERSET_BASED">На основе суперсетов</option>
            </Select>
          </Field>
        </div>
        <div className="mt-4">
          <Field label="Примечание (блок внизу плана)">
            <TextArea
              value={draft.notes}
              onChange={(e) => patch((d) => (d.notes = e.target.value))}
            />
          </Field>
        </div>
      </div>

      <ErrorBox error={mutErr} />

      {draft.blocks.map((block, bi) => (
        <div
          key={bi}
          className={`rounded-lg border p-4 ${
            block.block_type === "SUPERSET"
              ? "border-amber-300 bg-amber-50"
              : "border-slate-200 bg-white"
          }`}
        >
          <div className="mb-3 flex flex-wrap items-center gap-2">
            <Badge color={block.block_type === "SUPERSET" ? "amber" : "indigo"}>
              Блок {bi + 1}
            </Badge>
            <Select
              value={block.block_type}
              onChange={(e) => setBlockType(bi, e.target.value as BlockType)}
              className="!w-auto"
            >
              <option value="SINGLE">Одиночное упражнение</option>
              <option value="SUPERSET">Суперсет</option>
            </Select>
            {block.block_type === "SUPERSET" && (
              <TextInput
                placeholder="Заметка к суперсету (напр. «Делаешь суперсетом»)"
                value={block.note}
                onChange={(e) => patch((d) => (d.blocks[bi].note = e.target.value))}
                className="max-w-xs"
              />
            )}
            <div className="ml-auto flex gap-1">
              <Button variant="ghost" onClick={() => patch((d) => moveItem(d.blocks, bi, -1))}>
                ↑
              </Button>
              <Button variant="ghost" onClick={() => patch((d) => moveItem(d.blocks, bi, 1))}>
                ↓
              </Button>
              <Button variant="ghost" onClick={() => patch((d) => d.blocks.splice(bi, 1))}>
                🗑
              </Button>
            </div>
          </div>

          <div className="space-y-3">
            {block.units.map((unit, ui) => (
              <UnitEditor
                key={ui}
                unit={unit}
                groups={groups}
                exercises={exercises}
                onChange={(fn) => patch((d) => fn(d.blocks[bi].units[ui]))}
                onRemove={
                  block.units.length > 1
                    ? () => patch((d) => d.blocks[bi].units.splice(ui, 1))
                    : undefined
                }
              />
            ))}
          </div>

          {block.block_type === "SUPERSET" && (
            <Button
              variant="secondary"
              className="mt-3"
              onClick={() => patch((d) => d.blocks[bi].units.push(newUnit()))}
            >
              + Упражнение в суперсет
            </Button>
          )}
        </div>
      ))}

      <div className="flex gap-2">
        <Button
          variant="secondary"
          onClick={() =>
            patch((d) =>
              d.blocks.push({ block_type: "SINGLE", note: "", units: [newUnit()] }),
            )
          }
        >
          + Одиночное упражнение
        </Button>
        <Button
          variant="secondary"
          onClick={() =>
            patch((d) =>
              d.blocks.push({
                block_type: "SUPERSET",
                note: "Делаешь суперсетом.",
                units: [newUnit(), newUnit()],
              }),
            )
          }
        >
          + Суперсет
        </Button>
      </div>
    </div>
  );
}

function moveItem<T>(arr: T[], index: number, delta: number) {
  const target = index + delta;
  if (target < 0 || target >= arr.length) return;
  [arr[index], arr[target]] = [arr[target], arr[index]];
}

function UnitEditor({
  unit,
  groups,
  exercises,
  onChange,
  onRemove,
}: {
  unit: DraftUnit;
  groups: MuscleGroup[];
  exercises: Exercise[];
  onChange: (fn: (u: DraftUnit) => void) => void;
  onRemove?: () => void;
}) {
  // Derive the muscle group from the currently-selected exercise.
  const selectedExercise = exercises.find((e) => e.id === unit.exercise_id) ?? null;
  const [groupId, setGroupId] = useState<number | null>(
    selectedExercise?.muscle_group_id ?? null,
  );

  const groupOptions = groups.map((g) => ({ id: g.id, label: g.name }));
  const exerciseOptions = exercises
    .filter((e) => e.muscle_group_id === groupId)
    .map((e) => ({ id: e.id, label: e.name }));

  return (
    <div className="rounded-md border border-slate-200 bg-white p-3">
      <div className="flex flex-wrap items-end gap-2">
        <div className="min-w-48 flex-1">
          <span className="mb-1 block text-xs font-medium text-slate-500">
            Группа мышц
          </span>
          <Combobox
            options={groupOptions}
            value={groupId}
            placeholder="Начните вводить…"
            onChange={(gid) => {
              setGroupId(gid);
              // Reset the exercise if it no longer belongs to the chosen group.
              const belongs = exercises.some(
                (e) => e.id === unit.exercise_id && e.muscle_group_id === gid,
              );
              if (!belongs) onChange((u) => (u.exercise_id = 0));
            }}
          />
        </div>
        <div className="min-w-56 flex-1">
          <span className="mb-1 block text-xs font-medium text-slate-500">
            Упражнение
          </span>
          <Combobox
            options={exerciseOptions}
            value={unit.exercise_id || null}
            disabled={groupId == null}
            placeholder={groupId == null ? "Сначала выберите группу" : "Начните вводить…"}
            onChange={(exId) => onChange((u) => (u.exercise_id = exId))}
          />
        </div>
        <label className="flex items-center gap-1 pb-1.5 text-sm text-green-700">
          <input
            type="checkbox"
            checked={unit.highlight}
            onChange={(e) => onChange((u) => (u.highlight = e.target.checked))}
          />
          снять на видео
        </label>
        {onRemove && (
          <Button variant="ghost" className="pb-1.5" onClick={onRemove}>
            🗑
          </Button>
        )}
      </div>

      <div className="mt-2">
        <TextInput
          placeholder="Заметка к упражнению (напр. «По 5 раз на руку»)"
          value={unit.note}
          onChange={(e) => onChange((u) => (u.note = e.target.value))}
        />
      </div>

      <div className="mt-2 space-y-1.5">
        <div className="text-xs font-medium text-slate-400">Подходы</div>
        {unit.entries.map((entry, ei) => (
          <EntryRow
            key={ei}
            entry={entry}
            onChange={(fn) => onChange((u) => fn(u.entries[ei]))}
            onRemove={
              unit.entries.length > 1
                ? () => onChange((u) => u.entries.splice(ei, 1))
                : undefined
            }
          />
        ))}
        <Button
          variant="ghost"
          className="!px-1 text-indigo-600"
          onClick={() => onChange((u) => u.entries.push(newEntry()))}
        >
          + подход
        </Button>
      </div>
    </div>
  );
}

function EntryRow({
  entry,
  onChange,
  onRemove,
}: {
  entry: DraftEntry;
  onChange: (fn: (e: DraftEntry) => void) => void;
  onRemove?: () => void;
}) {
  const numInput = "w-16";
  return (
    <div className="flex flex-wrap items-center gap-2 rounded bg-slate-50 px-2 py-1.5 text-sm">
      <Select
        value={entry.kind}
        onChange={(e) => onChange((x) => (x.kind = e.target.value as PlanExerciseKind))}
        className="!w-auto"
      >
        <option value="WEIGHT">Вес/повторы</option>
        <option value="TIME">Время</option>
      </Select>
      <span className="text-slate-500">подходов</span>
      <TextInput
        type="number"
        min={1}
        value={entry.sets}
        onChange={(e) => onChange((x) => (x.sets = Number(e.target.value)))}
        className={numInput}
      />
      {entry.kind === "WEIGHT" ? (
        <>
          <span className="text-slate-500">×</span>
          <TextInput
            type="number"
            min={1}
            value={entry.reps ?? ""}
            onChange={(e) => onChange((x) => (x.reps = e.target.value === "" ? null : Number(e.target.value)))}
            className={numInput}
          />
          <span className="text-slate-500">повт.</span>
          <TextInput
            type="number"
            min={0}
            step="0.5"
            placeholder="кг"
            value={entry.weight}
            onChange={(e) => onChange((x) => (x.weight = e.target.value))}
            className="w-20"
          />
          <span className="text-slate-500">кг (пусто = свой вес)</span>
        </>
      ) : (
        <>
          <span className="text-slate-500">×</span>
          <TextInput
            type="number"
            min={1}
            value={entry.duration ?? ""}
            onChange={(e) =>
              onChange((x) => (x.duration = e.target.value === "" ? null : Number(e.target.value)))
            }
            className={numInput}
          />
          <span className="text-slate-500">сек</span>
        </>
      )}
      {onRemove && (
        <button onClick={onRemove} className="ml-auto text-slate-400 hover:text-red-600">
          ✕
        </button>
      )}
    </div>
  );
}
