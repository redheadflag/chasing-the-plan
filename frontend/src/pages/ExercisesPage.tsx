import { useMemo, useState } from "react";
import {
  useExerciseMutations,
  useExercises,
  useMuscleGroups,
  useMuscleGroupMutations,
} from "../api/hooks";
import type { Exercise, MuscleGroup } from "../api/types";
import { Badge, Button, ErrorBox, Field, Modal, Select, Spinner, TextInput } from "../components/ui";

export default function ExercisesPage() {
  const [groupFilter, setGroupFilter] = useState<number | "">("");
  const [search, setSearch] = useState("");
  const [editing, setEditing] = useState<Exercise | "new" | null>(null);
  const [showGroups, setShowGroups] = useState(false);

  const groupsQ = useMuscleGroups();
  const params = useMemo(
    () => ({
      muscle_group_id: groupFilter === "" ? undefined : groupFilter,
      q: search.trim() || undefined,
    }),
    [groupFilter, search],
  );
  const exercisesQ = useExercises(params);
  const { remove } = useExerciseMutations();

  return (
    <div>
      <div className="mb-5 flex flex-wrap items-center justify-between gap-2">
        <h1 className="text-2xl font-bold">Упражнения</h1>
        <div className="flex gap-2">
          <Button variant="secondary" onClick={() => setShowGroups(true)}>
            Группы мышц
          </Button>
          <Button onClick={() => setEditing("new")}>+ Упражнение</Button>
        </div>
      </div>

      <div className="mb-4 flex flex-wrap gap-3">
        <Select
          value={groupFilter}
          onChange={(e) => setGroupFilter(e.target.value === "" ? "" : Number(e.target.value))}
          className="max-w-xs"
        >
          <option value="">Все группы мышц</option>
          {groupsQ.data?.map((g) => (
            <option key={g.id} value={g.id}>
              {g.name}
            </option>
          ))}
        </Select>
        <TextInput
          placeholder="Поиск по названию…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="max-w-xs"
        />
      </div>

      <ErrorBox error={exercisesQ.error} />

      {exercisesQ.isLoading ? (
        <Spinner />
      ) : (
        <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-left text-slate-500">
              <tr>
                <th className="px-4 py-2 font-medium">Название</th>
                <th className="px-4 py-2 font-medium">Группа мышц</th>
                <th className="hidden px-4 py-2 font-medium sm:table-cell">Ссылка</th>
                <th className="px-4 py-2" />
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {exercisesQ.data?.map((ex) => (
                <tr key={ex.id} className="hover:bg-slate-50">
                  <td className="px-4 py-2 font-medium">{ex.name}</td>
                  <td className="px-4 py-2">
                    <Badge color="indigo">{ex.muscle_group?.name ?? "—"}</Badge>
                  </td>
                  <td className="hidden max-w-xs truncate px-4 py-2 text-slate-500 sm:table-cell">
                    {ex.url ? (
                      <a
                        href={ex.url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-indigo-600 hover:underline"
                      >
                        {ex.url}
                      </a>
                    ) : (
                      "—"
                    )}
                  </td>
                  <td className="px-4 py-2 text-right whitespace-nowrap">
                    <Button variant="ghost" onClick={() => setEditing(ex)}>
                      ✎
                    </Button>
                    <Button
                      variant="ghost"
                      onClick={() => {
                        if (confirm(`Удалить «${ex.name}»?`)) remove.mutate(ex.id);
                      }}
                    >
                      🗑
                    </Button>
                  </td>
                </tr>
              ))}
              {exercisesQ.data?.length === 0 && (
                <tr>
                  <td colSpan={4} className="px-4 py-8 text-center text-slate-400">
                    Ничего не найдено
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {editing && (
        <ExerciseModal
          exercise={editing === "new" ? null : editing}
          groups={groupsQ.data ?? []}
          onClose={() => setEditing(null)}
        />
      )}
      {showGroups && <GroupsModal onClose={() => setShowGroups(false)} />}
    </div>
  );
}

function ExerciseModal({
  exercise,
  groups,
  onClose,
}: {
  exercise: Exercise | null;
  groups: MuscleGroup[];
  onClose: () => void;
}) {
  const { create, update } = useExerciseMutations();
  const [name, setName] = useState(exercise?.name ?? "");
  const [url, setUrl] = useState(exercise?.url ?? "");
  const [groupId, setGroupId] = useState<number | "">(
    exercise?.muscle_group_id ?? groups[0]?.id ?? "",
  );
  const mut = exercise ? update : create;

  const submit = () => {
    if (!name.trim() || groupId === "") return;
    const payload = { name: name.trim(), url: url.trim() || null, muscle_group_id: groupId };
    if (exercise) {
      update.mutate({ id: exercise.id, ...payload }, { onSuccess: onClose });
    } else {
      create.mutate(payload, { onSuccess: onClose });
    }
  };

  return (
    <Modal title={exercise ? "Изменить упражнение" : "Новое упражнение"} onClose={onClose}>
      <div className="space-y-4">
        <Field label="Название">
          <TextInput value={name} onChange={(e) => setName(e.target.value)} autoFocus />
        </Field>
        <Field label="Группа мышц">
          <Select
            value={groupId}
            onChange={(e) => setGroupId(e.target.value === "" ? "" : Number(e.target.value))}
          >
            {groups.map((g) => (
              <option key={g.id} value={g.id}>
                {g.name}
              </option>
            ))}
          </Select>
        </Field>
        <Field label="Ссылка на упражнение (URL)">
          <TextInput
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://…"
          />
        </Field>
        <ErrorBox error={mut.error} />
        <div className="flex justify-end gap-2">
          <Button variant="secondary" onClick={onClose}>
            Отмена
          </Button>
          <Button onClick={submit} disabled={mut.isPending}>
            Сохранить
          </Button>
        </div>
      </div>
    </Modal>
  );
}

function GroupsModal({ onClose }: { onClose: () => void }) {
  const groupsQ = useMuscleGroups();
  const { create, update, remove } = useMuscleGroupMutations();
  const [newName, setNewName] = useState("");

  return (
    <Modal title="Группы мышц" onClose={onClose}>
      <div className="space-y-3">
        <div className="flex gap-2">
          <TextInput
            placeholder="Новая группа…"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
          />
          <Button
            onClick={() => {
              if (newName.trim())
                create.mutate({ name: newName.trim() }, { onSuccess: () => setNewName("") });
            }}
          >
            Добавить
          </Button>
        </div>
        <ErrorBox error={create.error ?? remove.error} />
        <ul className="max-h-72 divide-y divide-slate-100 overflow-y-auto rounded-md border border-slate-200">
          {groupsQ.data?.map((g) => (
            <li key={g.id} className="flex items-center justify-between px-3 py-2 text-sm">
              <input
                defaultValue={g.name}
                className="mr-2 flex-1 rounded border border-transparent px-1 py-0.5 hover:border-slate-300 focus:border-indigo-400 focus:outline-none"
                onBlur={(e) => {
                  if (e.target.value.trim() && e.target.value !== g.name)
                    update.mutate({ id: g.id, name: e.target.value.trim() });
                }}
              />
              <Button
                variant="ghost"
                onClick={() => {
                  if (confirm(`Удалить группу «${g.name}»? Упражнения группы тоже удалятся.`))
                    remove.mutate(g.id);
                }}
              >
                🗑
              </Button>
            </li>
          ))}
        </ul>
      </div>
    </Modal>
  );
}
