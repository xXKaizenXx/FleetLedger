import { FormEvent, useEffect, useState } from "react";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";
import type { AuditLog, Paginated, Transaction, Vehicle } from "../types";

export function DashboardPage() {
  const { effectiveTenantId, canManage, user } = useAuth();
  const [stats, setStats] = useState({ vehicles: 0, transactions: 0, audits: 0, spend: 0 });
  const [reportMsg, setReportMsg] = useState("");
  const [year, setYear] = useState(new Date().getFullYear());
  const [month, setMonth] = useState(new Date().getMonth() + 1);

  useEffect(() => {
    if (!effectiveTenantId && user?.role === "super_admin") return;

    const opts = { tenantId: effectiveTenantId };
    Promise.all([
      api<Paginated<Vehicle>>("/vehicles/", opts),
      api<Paginated<Transaction>>("/transactions/", opts),
      api<Paginated<AuditLog>>("/audit-logs/", opts),
    ])
      .then(([v, t, a]) => {
        const spend = t.results.reduce((s, x) => s + parseFloat(x.amount), 0);
        setStats({
          vehicles: v.count,
          transactions: t.count,
          audits: a.count,
          spend,
        });
      })
      .catch((err) => {
        console.error("Dashboard load failed:", err);
      });
  }, [effectiveTenantId, user?.role]);

  async function queueReport(e: FormEvent) {
    e.preventDefault();
    setReportMsg("");
    try {
      const res = await api<{ detail: string; task_id: string }>("/reports/monthly/", {
        method: "POST",
        body: JSON.stringify({ year, month }),
        tenantId: effectiveTenantId,
      });
      setReportMsg(res.detail);
    } catch (err) {
      setReportMsg(err instanceof Error ? err.message : "Failed to queue report");
    }
  }

  const needsTenant = user?.role === "super_admin" && !effectiveTenantId;

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <p className="text-slate-400">
          {user?.tenant_name || "Platform overview"} — {user?.role_display}
        </p>
      </header>

      {needsTenant && (
        <div className="rounded-lg border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-200">
          Select a tenant in the sidebar to view scoped data.
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: "Vehicles", value: stats.vehicles },
          { label: "Transactions", value: stats.transactions },
          { label: "Audit events", value: stats.audits },
          { label: "Period spend", value: `$${stats.spend.toLocaleString()}` },
        ].map((s) => (
          <div key={s.label} className="card p-5">
            <p className="text-xs uppercase tracking-wide text-slate-500">{s.label}</p>
            <p className="mt-2 text-3xl font-bold text-white">{s.value}</p>
          </div>
        ))}
      </div>

      {canManage && (
        <div className="card p-6">
          <h2 className="text-lg font-semibold text-white">End-of-month statement</h2>
          <p className="mt-1 text-sm text-slate-400">
            Queues a Celery job — encrypted PDF emailed when ready.
          </p>
          <form className="mt-4 flex flex-wrap items-end gap-4" onSubmit={queueReport}>
            <label className="text-sm text-slate-400">
              Year
              <input
                type="number"
                className="input mt-1 w-28"
                value={year}
                onChange={(e) => setYear(Number(e.target.value))}
              />
            </label>
            <label className="text-sm text-slate-400">
              Month
              <input
                type="number"
                min={1}
                max={12}
                className="input mt-1 w-20"
                value={month}
                onChange={(e) => setMonth(Number(e.target.value))}
              />
            </label>
            <button type="submit" className="btn-primary" disabled={needsTenant}>
              Generate & email report
            </button>
          </form>
          {reportMsg && <p className="mt-3 text-sm text-brand-400">{reportMsg}</p>}
        </div>
      )}
    </div>
  );
}
