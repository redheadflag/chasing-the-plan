import { useEffect, useMemo, useRef, useState } from "react";

export interface ComboOption {
  id: number;
  label: string;
}

/**
 * A text field with type-ahead suggestions. Shows options whose label contains
 * the typed text; clicking one selects it.
 */
export function Combobox({
  options,
  value,
  onChange,
  placeholder,
  disabled,
  autoFocus,
}: {
  options: ComboOption[];
  value: number | null;
  onChange: (id: number) => void;
  placeholder?: string;
  disabled?: boolean;
  autoFocus?: boolean;
}) {
  const selected = options.find((o) => o.id === value) ?? null;
  const [query, setQuery] = useState(selected?.label ?? "");
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(0);
  const boxRef = useRef<HTMLDivElement>(null);

  // Keep the visible text in sync when the selected option changes externally.
  useEffect(() => {
    setQuery(selected?.label ?? "");
  }, [selected?.id]); // eslint-disable-line react-hooks/exhaustive-deps

  // Close when clicking outside.
  useEffect(() => {
    const onDoc = (e: MouseEvent) => {
      if (boxRef.current && !boxRef.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, []);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    const matches = q
      ? options.filter((o) => o.label.toLowerCase().includes(q))
      : options;
    return matches.slice(0, 50);
  }, [options, query]);

  const select = (opt: ComboOption) => {
    onChange(opt.id);
    setQuery(opt.label);
    setOpen(false);
  };

  const inputBase =
    "w-full rounded-md border px-3 py-1.5 text-sm outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 disabled:bg-slate-100";
  const invalid = value == null && !disabled;

  return (
    <div className="relative" ref={boxRef}>
      <input
        className={`${inputBase} ${invalid ? "border-amber-400" : "border-slate-300"}`}
        value={query}
        placeholder={placeholder}
        disabled={disabled}
        autoFocus={autoFocus}
        onFocus={() => setOpen(true)}
        onChange={(e) => {
          setQuery(e.target.value);
          setOpen(true);
          setActive(0);
        }}
        onKeyDown={(e) => {
          if (e.key === "ArrowDown") {
            setOpen(true);
            setActive((a) => Math.min(a + 1, filtered.length - 1));
            e.preventDefault();
          } else if (e.key === "ArrowUp") {
            setActive((a) => Math.max(a - 1, 0));
            e.preventDefault();
          } else if (e.key === "Enter" && open && filtered[active]) {
            select(filtered[active]);
            e.preventDefault();
          } else if (e.key === "Escape") {
            setOpen(false);
          }
        }}
      />
      {open && filtered.length > 0 && (
        <ul className="absolute z-20 mt-1 max-h-60 w-full overflow-y-auto rounded-md border border-slate-200 bg-white py-1 shadow-lg">
          {filtered.map((opt, i) => (
            <li
              key={opt.id}
              onMouseDown={(e) => {
                e.preventDefault();
                select(opt);
              }}
              onMouseEnter={() => setActive(i)}
              className={`cursor-pointer px-3 py-1.5 text-sm ${
                i === active ? "bg-indigo-50 text-indigo-700" : "hover:bg-slate-50"
              } ${opt.id === value ? "font-semibold" : ""}`}
            >
              {opt.label}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
