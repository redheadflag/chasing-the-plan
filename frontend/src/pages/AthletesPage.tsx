import { useState } from "react";
import { Link } from "react-router-dom";
import { useAthleteMutations, useAthletes } from "../api/hooks";
import type { Athlete } from "../api/types";
import { Button, ErrorBox, Field, Modal, Spinner, TextArea, TextInput } from "../components/ui";

export default function AthletesPage() {
  const athletesQ = useAthletes();
  const { remove } = useAthleteMutations();
  const [editing, setEditing] = useState<Athlete | "new" | null>(null);

  return (
    <div>
      <div className="mb-5 flex items-center justify-between">
        <h1 className="text-2xl font-bold">Атлеты</h1>
        <Button onClick={() => setEditing("new")}>+ Атлет</Button>
      </div>

      <ErrorBox error={athletesQ.error} />

      {athletesQ.isLoading ? (
        <Spinner />
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {athletesQ.data?.map((a) => (
            <div key={a.id} className="rounded-lg border border-slate-200 bg-white p-4">
              <div className="flex items-start justify-between">
                <div className="text-lg font-semibold">{a.name}</div>
                <div className="flex">
                  <Button variant="ghost" onClick={() => setEditing(a)}>
                    ✎
                  </Button>
                  <Button
                    variant="ghost"
                    onClick={() => {
                      if (confirm(`Удалить атлета «${a.name}»?`)) remove.mutate(a.id);
                    }}
                  >
                    🗑
                  </Button>
                </div>
              </div>
              {a.note && <p className="mt-1 text-sm text-slate-500">{a.note}</p>}
              <Link
                to={`/plans?athlete=${a.id}`}
                className="mt-3 inline-block text-sm font-medium text-indigo-600 hover:underline"
              >
                Открыть план →
              </Link>
            </div>
          ))}
          {athletesQ.data?.length === 0 && (
            <div className="col-span-full rounded-lg border border-dashed border-slate-300 p-8 text-center text-slate-400">
              Пока нет атлетов
            </div>
          )}
        </div>
      )}

      {editing && (
        <AthleteModal
          athlete={editing === "new" ? null : editing}
          onClose={() => setEditing(null)}
        />
      )}
    </div>
  );
}

function AthleteModal({ athlete, onClose }: { athlete: Athlete | null; onClose: () => void }) {
  const { create, update } = useAthleteMutations();
  const [name, setName] = useState(athlete?.name ?? "");
  const [note, setNote] = useState(athlete?.note ?? "");
  const mut = athlete ? update : create;

  const submit = () => {
    if (!name.trim()) return;
    const payload = { name: name.trim(), note: note.trim() || null };
    if (athlete) update.mutate({ id: athlete.id, ...payload }, { onSuccess: onClose });
    else create.mutate(payload, { onSuccess: onClose });
  };

  return (
    <Modal title={athlete ? "Изменить атлета" : "Новый атлет"} onClose={onClose}>
      <div className="space-y-4">
        <Field label="Имя">
          <TextInput value={name} onChange={(e) => setName(e.target.value)} autoFocus />
        </Field>
        <Field label="Заметка">
          <TextArea value={note} onChange={(e) => setNote(e.target.value)} />
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
