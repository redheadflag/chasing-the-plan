import { NavLink, Outlet } from "react-router-dom";

const links = [
  { to: "/exercises", label: "Упражнения", icon: "🏋️" },
  { to: "/athletes", label: "Атлеты", icon: "🧑" },
  { to: "/plans", label: "Планы", icon: "📄" },
];

export default function Layout() {
  return (
    <div className="flex h-full">
      <aside className="flex w-60 shrink-0 flex-col border-r border-slate-200 bg-white">
        <div className="border-b border-slate-200 px-5 py-4">
          <div className="text-lg font-bold text-indigo-700">Chasing the Plan</div>
          <div className="text-xs text-slate-400">Генератор планов тренировок</div>
        </div>
        <nav className="flex flex-col gap-1 p-3">
          {links.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              className={({ isActive }) =>
                `flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium ${
                  isActive
                    ? "bg-indigo-50 text-indigo-700"
                    : "text-slate-600 hover:bg-slate-100"
                }`
              }
            >
              <span>{l.icon}</span>
              {l.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-6xl p-6">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
