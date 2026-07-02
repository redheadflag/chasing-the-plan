import { useState } from "react";
import { NavLink, Outlet } from "react-router-dom";

const links = [
  { to: "/exercises", label: "Упражнения", icon: "🏋️" },
  { to: "/athletes", label: "Атлеты", icon: "🧑" },
  { to: "/plans", label: "Планы", icon: "📄" },
];

function NavLinks({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <nav className="flex flex-col gap-1 p-3">
      {links.map((l) => (
        <NavLink
          key={l.to}
          to={l.to}
          onClick={onNavigate}
          className={({ isActive }) =>
            `flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium ${
              isActive ? "bg-indigo-50 text-indigo-700" : "text-slate-600 hover:bg-slate-100"
            }`
          }
        >
          <span>{l.icon}</span>
          {l.label}
        </NavLink>
      ))}
    </nav>
  );
}

function Brand() {
  return (
    <div>
      <div className="text-lg font-bold text-indigo-700">Chasing the Plan</div>
      <div className="text-xs text-slate-400">Генератор планов тренировок</div>
    </div>
  );
}

export default function Layout() {
  const [drawerOpen, setDrawerOpen] = useState(false);

  return (
    <div className="flex h-full flex-col md:flex-row">
      {/* Mobile top bar */}
      <header className="flex items-center gap-3 border-b border-slate-200 bg-white px-4 py-3 md:hidden">
        <button
          onClick={() => setDrawerOpen(true)}
          aria-label="Открыть меню"
          className="-ml-1 rounded-md p-1 text-2xl leading-none text-slate-600 hover:bg-slate-100"
        >
          ☰
        </button>
        <span className="text-base font-bold text-indigo-700">Chasing the Plan</span>
      </header>

      {/* Desktop sidebar */}
      <aside className="hidden w-60 shrink-0 flex-col border-r border-slate-200 bg-white md:flex">
        <div className="border-b border-slate-200 px-5 py-4">
          <Brand />
        </div>
        <NavLinks />
      </aside>

      {/* Mobile drawer */}
      {drawerOpen && (
        <div className="fixed inset-0 z-40 md:hidden" onClick={() => setDrawerOpen(false)}>
          <div className="absolute inset-0 bg-black/40" />
          <aside
            className="absolute left-0 top-0 flex h-full w-64 flex-col bg-white shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4">
              <Brand />
              <button
                onClick={() => setDrawerOpen(false)}
                aria-label="Закрыть меню"
                className="text-slate-400 hover:text-slate-700"
              >
                ✕
              </button>
            </div>
            <NavLinks onNavigate={() => setDrawerOpen(false)} />
          </aside>
        </div>
      )}

      <main className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-6xl p-4 md:p-6">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
