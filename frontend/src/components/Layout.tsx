import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const nav = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/vehicles", label: "Vehicles" },
  { to: "/transactions", label: "Transactions" },
  { to: "/audit", label: "Audit Trail" },
];

export function Layout() {
  const { user, logout, organizations, tenantOverride, setTenantOverride, effectiveTenantId } =
    useAuth();

  return (
    <div className="flex min-h-screen">
      <aside className="flex w-60 flex-col border-r border-slate-800 bg-slate-900/80 p-4">
        <div className="mb-8">
          <p className="text-xs font-medium uppercase tracking-widest text-brand-400">FleetLedger</p>
          <h1 className="text-lg font-bold text-white">Finance & Compliance</h1>
        </div>

        <nav className="flex flex-1 flex-col gap-1">
          {nav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `rounded-lg px-3 py-2 text-sm font-medium transition ${
                  isActive
                    ? "bg-brand-500/15 text-brand-400"
                    : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="mt-auto space-y-3 border-t border-slate-800 pt-4">
          {user?.role === "super_admin" && organizations.length > 0 && (
            <label className="block text-xs text-slate-500">
              Tenant scope
              <select
                className="input mt-1"
                value={tenantOverride ?? ""}
                onChange={(e) =>
                  setTenantOverride(e.target.value ? Number(e.target.value) : null)
                }
              >
                <option value="">Select tenant to view data</option>
                {organizations.map((o) => (
                  <option key={o.id} value={o.id}>
                    {o.name}
                  </option>
                ))}
              </select>
            </label>
          )}
          <div className="text-xs text-slate-500">
            <p className="font-medium text-slate-300">{user?.username}</p>
            <p>{user?.role_display}</p>
            {user?.tenant_name && <p>{user.tenant_name}</p>}
            {effectiveTenantId && user?.role === "super_admin" && (
              <p className="font-mono text-brand-400">Scoped: #{effectiveTenantId}</p>
            )}
          </div>
          <button type="button" className="btn-ghost w-full" onClick={() => logout()}>
            Sign out
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-auto p-8">
        <Outlet />
      </main>
    </div>
  );
}

