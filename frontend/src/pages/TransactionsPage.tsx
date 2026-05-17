import { useEffect, useState } from "react";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";
import type { Paginated, Transaction } from "../types";

export function TransactionsPage() {
  const { effectiveTenantId, user } = useAuth();
  const [rows, setRows] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user?.role === "super_admin" && !effectiveTenantId) {
      setRows([]);
      setLoading(false);
      return;
    }
    setLoading(true);
    api<Paginated<Transaction>>("/transactions/", { tenantId: effectiveTenantId })
      .then((d) => setRows(d.results))
      .finally(() => setLoading(false));
  }, [effectiveTenantId, user?.role]);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white">Financial transactions</h1>
      <div className="card overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-slate-800 bg-slate-900/80 text-xs uppercase text-slate-500">
            <tr>
              <th className="px-4 py-3">Date</th>
              <th className="px-4 py-3">Type</th>
              <th className="px-4 py-3">Amount</th>
              <th className="px-4 py-3">Reference</th>
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
                  No transactions in scope.
                </td>
              </tr>
            )}
            {rows.map((t) => (
              <tr key={t.id} className="border-b border-slate-800/60 hover:bg-slate-800/30">
                <td className="px-4 py-3">{t.occurred_at}</td>
                <td className="px-4 py-3 capitalize">{t.transaction_type.replace("_", " ")}</td>
                <td className="px-4 py-3 font-mono text-emerald-400">
                  ${parseFloat(t.amount).toLocaleString()}
                </td>
                <td className="px-4 py-3 text-slate-400">{t.reference || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
