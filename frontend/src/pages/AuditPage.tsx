import { useEffect, useState } from "react";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";
import type { AuditLog, Paginated } from "../types";

export function AuditPage() {
  const { effectiveTenantId, user } = useAuth();
  const [rows, setRows] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user?.role === "super_admin" && !effectiveTenantId) {
      setRows([]);
      setLoading(false);
      return;
    }
    setLoading(true);
    api<Paginated<AuditLog>>("/audit-logs/", { tenantId: effectiveTenantId })
      .then((d) => setRows(d.results))
      .finally(() => setLoading(false));
  }, [effectiveTenantId, user?.role]);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white">Immutable audit trail</h1>
      <p className="text-sm text-slate-400">Append-only log of fleet and financial changes.</p>
      <div className="card overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-slate-800 bg-slate-900/80 text-xs uppercase text-slate-500">
            <tr>
              <th className="px-4 py-3">When</th>
              <th className="px-4 py-3">Action</th>
              <th className="px-4 py-3">Model</th>
              <th className="px-4 py-3">Object</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr>
                <td colSpan={4} className="px-4 py-8 text-center text-slate-500">
                  Loading…
                </td>
              </tr>
            )}
            {!loading && rows.length === 0 && (
              <tr>
                <td colSpan={4} className="px-4 py-8 text-center text-slate-500">
                  No audit entries in scope.
                </td>
              </tr>
            )}
            {rows.map((a) => (
              <tr key={a.id} className="border-b border-slate-800/60 hover:bg-slate-800/30">
                <td className="px-4 py-3 text-xs text-slate-400">
                  {new Date(a.created_at).toLocaleString()}
                </td>
                <td className="px-4 py-3 capitalize">{a.action}</td>
                <td className="px-4 py-3 font-mono text-xs">{a.model_name}</td>
                <td className="px-4 py-3">{a.object_repr}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
